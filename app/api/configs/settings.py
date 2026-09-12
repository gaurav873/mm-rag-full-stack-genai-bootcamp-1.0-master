from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from pathlib import Path


class Settings(BaseSettings):
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
engine = create_engine(settings.DATABASE_URL)

BASE_DIR = Path(__file__).resolve().parents[2]

