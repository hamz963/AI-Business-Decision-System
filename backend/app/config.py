import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

# Look for .env in the project root (one level above backend/)
_ENV_FILE = BASE_DIR.parent / ".env"
if not _ENV_FILE.exists():
    _ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "AI-Powered Business Decision Support System (AI-BDSS)"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/ai_bdss.db"

    # Uploads & analytical data storage
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    DUCKDB_DIR: str = str(BASE_DIR / "duckdb_store")
    MAX_UPLOAD_BYTES: int = 100 * 1024 * 1024  # 100 MB hard cap per upload

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Free Tier AI / OpenCode Configuration
    ACTIVE_AI_MODEL: str = "big-pickle"
    GOOGLE_API_KEY: str = ""
    OPENCODE_API_KEY: str = "sk-WNmTxq7FltbxhDlMaXFWGXtDtwyBgkWW5KsnGEVJhDu4h03ESqZmpA27lcranOEP"
    OPENCODE_ZEN_BASE_URL: str = "https://opencode.ai/zen/v1"
    OLLAMA_BASE_URL: str = "http://localhost:11434"


settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.DUCKDB_DIR, exist_ok=True)
