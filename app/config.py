from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUMMARIZATION_API_URL: str | None = None
    EXTRACT_ENTITIES_API_URL: str | None = None
    QUESTION_GENERATION_API_URL: str | None = None
    MAX_TIMEOUT_CONNECT: int = 180 # seconds
    MAX_TIMEOUT_READ: int = 180 # seconds
    MAX_TIMEOUT_WRITE: int = 180 # seconds
    MAX_TIMEOUT_POOL: int = 180 # seconds

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()