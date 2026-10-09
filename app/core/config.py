from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application configuration"""
    
    APP_NAME :str = "geospatial-file-measurement-api"
    APP_VERSION : str = "0.1.0"
    API_PREFIX : str = "/api"
    DEBUG : bool = True

    DATABASE_URL : str 

    UPLOAD_DIR: str = "data/uploads"
    EXTRACTED_DIR: str = "data/extracted"

    MAX_FILE_SIZE_MB: int = 50

    ALLOWED_FILE_EXTENSIONS: tuple[str, ...] = (
        ".kml",
        ".zip",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()