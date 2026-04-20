from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "GoldScope API"
    environment: str = "development"
    database_url: str = "sqlite:///./goldscope.db"
    secret_key: str = Field(
        default="replace-with-a-long-random-secret",
        min_length=16,
    )
    access_token_expire_minutes: int = 24 * 60
    token_issuer: str = "goldscope-api"
    token_audience: str = "goldscope-users"
    algorithm: str = "HS256"
    gold_prices_source_name: str = "DataHub gold-prices snapshot (derived from WGC)"
    gold_prices_source_url: str = "https://datahub.io/core/gold-prices"
    public_base_url: str = "http://127.0.0.1:8000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        if value.startswith("postgres://"):
            return "postgresql+psycopg://" + value[len("postgres://") :]
        if value.startswith("postgresql://"):
            return "postgresql+psycopg://" + value[len("postgresql://") :]
        return value

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[3]

    @property
    def default_gold_prices_csv(self) -> Path:
        return self.project_root / "data" / "raw" / "gold_prices_monthly.csv"


@lru_cache
def get_settings() -> Settings:
    return Settings()
