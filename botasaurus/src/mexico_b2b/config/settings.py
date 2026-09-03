"""
Centralized settings management for the Mexico B2B Ingestion Pipeline.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file from project root if it exists
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


class Settings:
    """Application runtime settings and environment parameters."""

    PROJECT_ROOT: Path = PROJECT_ROOT
    CONFIG_DIR: Path = PROJECT_ROOT / "config"
    RAW_DATA_DIR: Path = PROJECT_ROOT / os.getenv("RAW_DATA_DIR", "data/raw")
    NORMALIZED_DATA_DIR: Path = PROJECT_ROOT / "data/normalized"
    OUTPUT_DIR: Path = PROJECT_ROOT / os.getenv("OUTPUT_DIR", "output")
    CACHE_DIR: Path = PROJECT_ROOT / os.getenv("CACHE_DIR", "cache")
    SOURCES_CONFIG_PATH: Path = CONFIG_DIR / "mexico_sources.yaml"

    # INEGI DENUE Token
    DENUE_API_TOKEN: Optional[str] = os.getenv("DENUE_API_TOKEN")

    # Ingestion & Network Concurrency
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "5"))
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    RETRY_MAX_ATTEMPTS: int = int(os.getenv("RETRY_MAX_ATTEMPTS", "3"))
    RETRY_BACKOFF_FACTOR: float = float(os.getenv("RETRY_BACKOFF_FACTOR", "2.0"))

    # Privacy and Compliance
    ENABLE_PERSONAL_CONTACT_FIELDS: bool = (
        os.getenv("ENABLE_PERSONAL_CONTACT_FIELDS", "false").lower() in ("true", "1", "yes")
    )

    # Entity Resolution & Merging Thresholds
    MIN_MERGE_CONFIDENCE: float = float(os.getenv("MIN_MERGE_CONFIDENCE", "0.95"))
    REVIEW_QUEUE_THRESHOLD: float = float(os.getenv("REVIEW_QUEUE_THRESHOLD", "0.80"))

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensures all runtime directories exist."""
        cls.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.NORMALIZED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
