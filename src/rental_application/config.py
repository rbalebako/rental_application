"""Configuration management for rental application filler."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Main configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="RENTAL_APP_",
        env_file=".env",
    )

    # Ollama/LLM settings
    ollama_host: str = "localhost:11434"
    ollama_model: str = "mistral"

    # Timeouts
    timeout_seconds: int = 30

    # Thresholds
    confidence_threshold: float = 0.7

    # Paths
    cache_dir: Path = Path.home() / ".cache" / "rental_application"

    # Features
    enable_ocr: bool = False
    verbose: bool = False

    # Localization
    language: str = "de"  # "de" for German, "en" for English, etc.
    date_format: str = "DD.MM.YYYY"  # Swiss/German date format


# Global config instance
config = Config()
