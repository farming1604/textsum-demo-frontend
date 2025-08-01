from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUMMARIZATION_API_URL: str | None = None
    EXTRACT_ENTITIES_API_URL: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()