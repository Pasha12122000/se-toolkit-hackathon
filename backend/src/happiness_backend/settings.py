from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = Field(default="Happiness Menu", alias="APP_NAME")
    debug: bool = Field(default=False, alias="APP_DEBUG")
    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    cors_origins_raw: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        alias="BACKEND_CORS_ORIGINS",
    )
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="happiness_menu", alias="DB_NAME")
    db_user: str = Field(default="happiness", alias="DB_USER")
    db_password: str = Field(default="happiness", alias="DB_PASSWORD")
    auth_secret: str = Field(default="dev-secret", alias="AUTH_SECRET")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @property
    def database_url(self) -> str:
        return (
            f"host={self.db_host} port={self.db_port} dbname={self.db_name} "
            f"user={self.db_user} password={self.db_password}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()

