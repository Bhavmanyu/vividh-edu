"""
IndiaLens backend configuration — reads from environment variables / .env file
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://indialens:indialens_dev@localhost:5432/indialens"
    database_url_sync: str = "postgresql://indialens:indialens_dev@localhost:5432/indialens"

    # Redis (Airflow broker + result backend)
    redis_url: str = "redis://localhost:6379/0"

    # FastAPI
    secret_key: str = "change-me-in-production-use-32-char-minimum"
    api_key_admin: str = "admin-dev-key-change-in-production"
    frontend_url: str = "http://localhost:3000"
    environment: str = "development"
    debug: bool = True

    # Scraper settings
    user_agent: str = "IndiaLensBot/1.0 (research; contact@indialens.in)"
    scrape_delay_seconds: float = 1.5     # politeness delay between requests
    anomaly_threshold_pct: float = 25.0   # flag deltas > 25%
    auto_accept_threshold_pct: float = 5.0  # auto-accept deltas < 5%

    # Reddit API (PRAW)
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "IndiaLensBot/1.0"

    # World Bank API
    worldbank_api_base: str = "https://api.worldbank.org/v2"

    # PPP factor (updated quarterly from World Bank)
    ppp_factor_inr_per_usd: float = 23.1

    # Model
    current_model_version: str = "v1.0-seed"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
