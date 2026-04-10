from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from itsdangerous import BadSignature, URLSafeSerializer

from happiness_backend.database import fetch_admin_by_username
from happiness_backend.settings import Settings, get_settings


@dataclass
class AuthenticatedAdmin:
    id: int
    username: str
    full_name: str
    title_ru: str
    title_en: str
    role: str

def create_token(username: str, settings: Settings) -> str:
    serializer = URLSafeSerializer(settings.auth_secret, salt="happiness-admin")
    return serializer.dumps({"username": username})


def _read_token(raw_header: str | None) -> str:
    if not raw_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token.")
    scheme, _, token = raw_header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token header.")
    return token


def get_current_admin(
    authorization: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> AuthenticatedAdmin:
    serializer = URLSafeSerializer(settings.auth_secret, salt="happiness-admin")
    token = _read_token(authorization)
    try:
        payload = serializer.loads(token)
    except BadSignature as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is not valid.") from exc

    admin = fetch_admin_by_username(payload["username"], settings)
    if admin is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found.")

    return AuthenticatedAdmin(**admin)


def require_owner(admin: AuthenticatedAdmin = Depends(get_current_admin)) -> AuthenticatedAdmin:
    if admin.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner access required.")
    return admin
