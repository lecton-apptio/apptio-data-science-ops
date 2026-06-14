"""Configuration management using Pydantic settings."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Ireland Apptio Operations Dashboard"
    app_version: str = "0.0.1"
    environment: Literal["development", "staging", "production"] = "production"
    debug: bool = False

    # DataDog
    dd_access_token: str = Field(default="", alias="DD_ACCESS_TOKEN")
    dd_site: str = Field(default="datadoghq.com", alias="DD_SITE")

    # Services to monitor
    services: list[str] = Field(
        default_factory=lambda: [
            "pythia",
            "pythia-slackbot",
            "pythia-insights",
            "expert-guidance-agent",
        ]
    )

    # Regions
    regions: list[str] = Field(default_factory=lambda: ["us-west-2", "eu-west-1", "ap-southeast-2"])

    # Metric targets
    p95_latency_target_ms: float = 100.0
    error_rate_target_percent: float = 1.0
    uptime_target_percent: float = 99.9

    # Server
    host: str = "0.0.0.0"
    port: int = 5000
    workers: int = 4

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def has_datadog_credentials(self) -> bool:
        """Check if DataDog credentials are configured."""
        return bool(self.dd_access_token)


# Global settings instance
settings = Settings()
