from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Default values keep local tooling (alembic/tests) usable out of the box.
    # In Docker/production these are overridden via environment variables.
    database_url: str = "postgresql+psycopg://clinic:clinic@localhost:5432/clinic"

    jwt_secret_key: str = "dev-secret-change-me"
    jwt_access_token_expires_minutes: int = 30
    jwt_refresh_token_expires_days: int = 14

    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
