import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for TerraSleuth OSINT engine."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # SerpApi Configuration
    SERPAPI_API_KEY: Optional[str] = None
    SERPAPI_BASE_URL: str = "https://serpapi.com/search"
    SERPAPI_TIMEOUT_SECONDS: int = 30

    # Cache & Persistence
    CACHE_DB_PATH: str = "terrasleuth.db"
    CACHE_ENABLED: bool = True
    CACHE_DEFAULT_TTL_HOURS: int = 168  # 7 days default cache for search payloads

    # Environment
    ENV: str = "development"
    DEBUG: bool = False

    # Optional Vision / LLM Keys for later sprints
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    def validate_serpapi_key(self) -> str:
        """Validate that SERPAPI_API_KEY is present for live queries."""
        key = self.SERPAPI_API_KEY or os.environ.get("SERPAPI_API_KEY")
        if not key or key.strip() == "" or "your_serpapi" in key.lower():
            raise ValueError(
                "SERPAPI_API_KEY is not configured. Please set SERPAPI_API_KEY in your environment or .env file."
            )
        return key.strip()


settings = Settings()
