from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "poe2-skill-gems"

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"


settings = Settings()
