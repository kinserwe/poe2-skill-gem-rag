from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "poe2-skill-gems"

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-3.1-flash-lite"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
