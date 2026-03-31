from functools import lru_cache
from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


def read_secret(secret_name: str, default: str = "") -> str:
    for base in (
        Path(f"/run/secrets"),
        Path(__file__).parent.parent.parent / "infra" / "secrets",
    ):
        path = base / \
            (secret_name if "/" in secret_name else f"{secret_name}.txt")
        if path.exists():
            return path.read_text().strip()
    return default


class Settings(BaseSettings):
    # ── Database ──
    DB_USER: str = "kosha"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "kosha_db"
    DB_PASSWORD: str = Field(
        default_factory=lambda: read_secret("db_password"))

    # ── Redis ──
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # ── Connector credentials ──
    YOUTUBE_API_KEY: str = Field(
        default_factory=lambda: read_secret("youtube_api_key"))
    EMAIL_USERNAME: str = Field(
        default_factory=lambda: read_secret("email_username"))
    EMAIL_PASSWORD: str = Field(
        default_factory=lambda: read_secret("email_password"))

    # ── API ──
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
