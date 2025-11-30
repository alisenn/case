import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Reperi AI Agent Backend"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://mongo:27017/")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "agent_logs")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL_ROUTER: str = os.getenv("OPENAI_MODEL_ROUTER", "gpt-4o-mini")
    OPENAI_MODEL_WORKER: str = os.getenv("OPENAI_MODEL_WORKER", "gpt-4o-mini")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "outputs")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_CSE_ID: str = os.getenv("GOOGLE_CSE_ID", "")

    class Config:
        env_file = ".env"

settings = Settings()
