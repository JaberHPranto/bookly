from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "localhost"
    REDIS_PORT: int = 6379

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")


Config = Settings()  # pyright: ignore[reportCallIssue]
