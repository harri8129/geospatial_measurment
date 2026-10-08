from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application configuration"""
    
    APP_NAME :str = "geospatial-file-measurement-api"
    APP_VERSION : str = "0.1.0"
    API_PREFIX : str = "/api"
    DEBUG : bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()