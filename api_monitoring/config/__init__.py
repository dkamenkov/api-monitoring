from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables with validation."""

    # API Endpoint Configuration
    endpoint_url: str = Field(..., description="The API endpoint to monitor")

    # AWS Credentials
    aws_access_key_id: str = Field(..., description="AWS Access Key ID")
    aws_secret_access_key: str = Field(..., description="AWS Secret Access Key")
    aws_default_region: str = Field("us-east-1", description="AWS Default Region")

    # Telegram Configuration
    telegram_bot_token: str = Field(..., description="Telegram Bot Token")
    telegram_chat_id: str = Field(..., description="Telegram Chat ID")

    # Application Configuration
    check_interval: int = Field(60, description="Interval between API checks in seconds")
    api_timeout: int = Field(15, description="Timeout for API requests in seconds")
    maintenance_check_timeout: int = Field(10, description="Timeout for maintenance check in seconds")
    log_level: str = Field("INFO", description="Logging level")
    log_file: Optional[str] = Field("logs.log", description="Log file path")

    @field_validator('endpoint_url')
    @classmethod
    def validate_endpoint_url(cls, v: str) -> str:
        """Ensure endpoint_url is properly formatted."""
        if not v.startswith(('http://', 'https://')):
            return f"https://{v}"
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Create a global settings instance
settings = Settings()
