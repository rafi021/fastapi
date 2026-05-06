from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ecommerce_db"
    SECRET_KEY: str = "change-me-in-production"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_TITLE: str = "E-Commerce API"
    APP_VERSION: str = "1.0.0"


settings = Settings()
