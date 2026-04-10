from typing import Literal

from pydantic import BaseModel, Field


Locale = Literal["ru", "en"]
Role = Literal["owner", "worker"]


class SectionSummary(BaseModel):
    id: str
    label: str
    category_count: int
    item_count: int


class CategorySummary(BaseModel):
    key: str
    label: str
    section_id: str
    item_count: int


class MenuItemOut(BaseModel):
    id: str
    name: str
    description: str
    price_rub: int
    category_label: str
    section_label: str
    is_popular: bool


class HighlightItem(BaseModel):
    id: str
    name: str
    category_label: str
    price_rub: int


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminProfile(BaseModel):
    username: str
    full_name: str
    title: str
    role: Role


class AdminLoginResponse(BaseModel):
    token: str
    profile: AdminProfile


class StaffMember(BaseModel):
    id: int
    username: str
    full_name: str
    title_ru: str
    title_en: str
    role: Role


class StaffSummary(BaseModel):
    total_admins: int
    owner_count: int
    worker_count: int
    members: list[StaffMember]


class MenuItemUpsert(BaseModel):
    id: str = Field(min_length=2)
    name_ru: str = Field(min_length=2)
    name_en: str = Field(min_length=2)
    category: str = Field(min_length=2)
    category_ru: str = Field(min_length=2)
    category_en: str = Field(min_length=2)
    section_id: Literal["food", "drinks", "sushi"]
    section_ru: str = Field(min_length=2)
    section_en: str = Field(min_length=2)
    price_rub: int = Field(ge=0)
    description_ru: str = Field(min_length=2)
    description_en: str = Field(min_length=2)
    is_popular: bool = False
    keywords: list[str] = Field(default_factory=list)


class StaffCreateRequest(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=6)
    full_name: str = Field(min_length=2)
    title_ru: str = Field(min_length=2)
    title_en: str = Field(min_length=2)

