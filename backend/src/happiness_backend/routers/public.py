from fastapi import APIRouter, Depends, Query

from happiness_backend.database import (
    fetch_categories,
    fetch_highlights,
    fetch_items,
    fetch_sections,
    search_items,
)
from happiness_backend.schemas import CategorySummary, HighlightItem, Locale, MenuItemOut, SectionSummary
from happiness_backend.settings import Settings, get_settings


router = APIRouter(prefix="/api")


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/menu/sections", response_model=list[SectionSummary])
def get_sections(
    locale: Locale = Query(default="ru"),
    settings: Settings = Depends(get_settings),
) -> list[SectionSummary]:
    return [SectionSummary(**row) for row in fetch_sections(locale, settings)]


@router.get("/menu/sections/{section_id}/categories", response_model=list[CategorySummary])
def get_categories(
    section_id: str,
    locale: Locale = Query(default="ru"),
    settings: Settings = Depends(get_settings),
) -> list[CategorySummary]:
    return [CategorySummary(**row) for row in fetch_categories(section_id, locale, settings)]


@router.get("/menu/categories/{category}/items", response_model=list[MenuItemOut])
def get_items(
    category: str,
    locale: Locale = Query(default="ru"),
    settings: Settings = Depends(get_settings),
) -> list[MenuItemOut]:
    return [MenuItemOut(**row) for row in fetch_items(category, locale, settings)]


@router.get("/menu/highlights", response_model=list[HighlightItem])
def get_highlights(
    locale: Locale = Query(default="ru"),
    settings: Settings = Depends(get_settings),
) -> list[HighlightItem]:
    return [HighlightItem(**row) for row in fetch_highlights(locale, settings)]


@router.get("/menu/search", response_model=list[MenuItemOut])
def search_menu_items(
    q: str,
    locale: Locale = Query(default="ru"),
    settings: Settings = Depends(get_settings),
) -> list[MenuItemOut]:
    return [MenuItemOut(**row) for row in search_items(q, locale, settings)]

