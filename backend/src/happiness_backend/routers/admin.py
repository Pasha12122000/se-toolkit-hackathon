from fastapi import APIRouter, Depends, HTTPException, status

from happiness_backend.auth import AuthenticatedAdmin, create_token, get_current_admin, require_owner
from happiness_backend.database import (
    create_or_update_item,
    create_worker,
    delete_item,
    delete_worker,
    fetch_menu_item_record,
    fetch_staff,
    verify_admin_credentials,
)
from happiness_backend.schemas import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminProfile,
    MenuItemUpsert,
    StaffCreateRequest,
    StaffMember,
    StaffSummary,
)
from happiness_backend.settings import Settings, get_settings


router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/login", response_model=AdminLoginResponse)
def login(
    payload: AdminLoginRequest,
    settings: Settings = Depends(get_settings),
) -> AdminLoginResponse:
    admin = verify_admin_credentials(payload.username, payload.password, settings)
    if admin is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong username or password.")

    profile = AdminProfile(
        username=admin["username"],
        full_name=admin["full_name"],
        title=admin["title_ru"],
        role=admin["role"],
    )
    return AdminLoginResponse(token=create_token(admin["username"], settings), profile=profile)


@router.get("/me", response_model=AdminProfile)
def get_me(admin: AuthenticatedAdmin = Depends(get_current_admin)) -> AdminProfile:
    return AdminProfile(
        username=admin.username,
        full_name=admin.full_name,
        title=admin.title_ru,
        role=admin.role,
    )


@router.get("/staff", response_model=StaffSummary)
def get_staff(
    admin: AuthenticatedAdmin = Depends(get_current_admin),
    settings: Settings = Depends(get_settings),
) -> StaffSummary:
    members = [StaffMember(**row) for row in fetch_staff(settings)]
    return StaffSummary(
        total_admins=len(members),
        owner_count=sum(1 for member in members if member.role == "owner"),
        worker_count=sum(1 for member in members if member.role == "worker"),
        members=members,
    )


@router.get("/items/{item_id}", response_model=MenuItemUpsert)
def get_menu_item_for_edit(
    item_id: str,
    admin: AuthenticatedAdmin = Depends(get_current_admin),
    settings: Settings = Depends(get_settings),
) -> MenuItemUpsert:
    record = fetch_menu_item_record(item_id, settings)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found.")
    return MenuItemUpsert(**record)


@router.post("/items")
def upsert_menu_item(
    payload: MenuItemUpsert,
    admin: AuthenticatedAdmin = Depends(get_current_admin),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    create_or_update_item(payload, settings)
    return {"status": "ok", "message": f"Menu item {payload.id} saved."}


@router.delete("/items/{item_id}")
def remove_menu_item(
    item_id: str,
    admin: AuthenticatedAdmin = Depends(get_current_admin),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    deleted = delete_item(item_id, settings)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found.")
    return {"status": "ok", "message": f"Menu item {item_id} deleted."}


@router.post("/staff")
def add_worker(
    payload: StaffCreateRequest,
    owner: AuthenticatedAdmin = Depends(require_owner),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    try:
        create_worker(payload, settings)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"status": "ok", "message": f"Worker {payload.username} added."}


@router.delete("/staff/{worker_id}")
def remove_worker(
    worker_id: int,
    owner: AuthenticatedAdmin = Depends(require_owner),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    deleted = delete_worker(worker_id, settings)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found.")
    return {"status": "ok", "message": f"Worker {worker_id} removed."}
