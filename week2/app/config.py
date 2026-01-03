"""Application configuration and settings."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Database settings
    db_path: Path = Path(__file__).resolve().parents[1] / "data" / "app.db"
    data_dir: Path = Path(__file__).resolve().parents[1] / "data"
    
    # Ollama settings
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    ollama_base_url: Optional[str] = os.getenv("OLLAMA_BASE_URL", None)
    
    # Application settings
    app_title: str = "Action Item Extractor"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"


# Global settings instance
settings = Settings()

