# backend/core/config.py

from functools import lru_cache
from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


def read_secret(secret_name: str, default: str = "") -> str:
    """Read a secret from Docker secrets or local dev fallback."""
    docker_path = Path(f"/run/secrets/{secret_name}")
    if docker_path.exists():
        return docker_path.read_text().strip()

    local_path = (
        Path(__file__).parent.parent.parent
        / "infra"
        / "secrets"
        / f"{secret_name}.txt"
    )
    if local_path.exists():
        return local_path.read_text().strip()

    return default


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────────
    DB_USER: str = "kosha"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "kosha_db"
    DB_PASSWORD: str = Field(default_factory=lambda: read_secret("db_password"))

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # ── MinIO ─────────────────────────────────────────────────────────────────
    MINIO_ROOT_USER: str = Field(
        default_factory=lambda: read_secret("minio_root_user")
    )
    MINIO_ROOT_PASSWORD: str = Field(
        default_factory=lambda: read_secret("minio_root_password")
    )

    # ── Connector credentials ─────────────────────────────────────────────────
    SPOTIFY_CLIENT_ID: str = Field(
        default_factory=lambda: read_secret("spotify_client_id")
    )
    SPOTIFY_CLIENT_SECRET: str = Field(
        default_factory=lambda: read_secret("spotify_client_secret")
    )
    # YouTube Data API key (for manual channel connector)
    YOUTUBE_API_KEY: str = Field(
        default_factory=lambda: read_secret("youtube_api_key")
    )
    # YouTube OAuth credentials (for subscriptions connector)
    YOUTUBE_CLIENT_ID: str = Field(
        default_factory=lambda: read_secret("youtube_client_id")
    )
    YOUTUBE_CLIENT_SECRET: str = Field(
        default_factory=lambda: read_secret("youtube_client_secret")
    )
    GITHUB_API_TOKEN: str = Field(
        default_factory=lambda: read_secret("github_api_token")
    )
    EMAIL_USERNAME: str = Field(
        default_factory=lambda: read_secret("email_username")
    )
    EMAIL_PASSWORD: str = Field(
        default_factory=lambda: read_secret("email_password")
    )

    # ── API ───────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

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
