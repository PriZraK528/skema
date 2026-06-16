from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    database_url: str = "postgresql+psycopg://clinic:clinic@localhost:5432/clinic"

    jwt_secret_key: str = "dev-secret-change-me"
    jwt_access_token_expires_minutes: int = 30
    jwt_refresh_token_expires_days: int = 14

    cors_origins: str = "http://localhost:5173"

    clinic_registration_key: str = "clinic-demo-key"

    enable_appointment_completer: bool = True
    appointment_complete_interval_seconds: int = 60

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return "postgresql+psycopg://" + value[len("postgresql://") :]
        if value.startswith("postgres://"):
            return "postgresql+psycopg://" + value[len("postgres://") :]
        return value

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
