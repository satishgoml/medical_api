from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Settings for the AI model configuration.
    Loads values from environment variables if available.
    """
    openai_api_key: Optional[str] = None
    default_model: str = "gpt-4o-mini"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Create a global instance for easy import
settings = Settings()