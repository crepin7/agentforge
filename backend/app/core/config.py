"""
AgentForge — Configuration centrale.
Charge les variables d'environnement avec validation Pydantic.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres globaux de la plateforme."""

    env: str = "development"
    debug: bool = True

    api_title: str = "AgentForge API"
    api_version: str = "1.0.0"
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    secret_key: str = "change-me-in-production-please-use-openssl-rand-base64-32"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7

    database_url: str = "postgresql+asyncpg://agentforge:agentforge@localhost:5432/agentforge"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    stripe_secret_key: str = "sk_test_replace_me"
    stripe_webhook_secret: str = "whsec_replace_me"
    stripe_publishable_key: str = "pk_test_replace_me"

    marketplace_fee_pct: float = 15.0
    free_tier_runs_per_month: int = 100
    pro_tier_price_cents: int = 2900
    enterprise_tier_price_cents: int = 99000

    sandbox_timeout_seconds: int = 30
    sandbox_max_memory_mb: int = 512
    sandbox_docker_image: str = "agentforge/sandbox:latest"

    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 100

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()