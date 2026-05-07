from dotenv import load_dotenv
from pydantic import BaseSettings
import os

load_dotenv()


class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017/elo"
    KAFKA_BOOTSTRAP_SERVERS: str | None = None
    KAFKA_SCHEMA_REGISTRY: str | None = None
    APP_ENV: str = "development"
    DEFAULT_K_FACTOR: int = 32
    DEFAULT_ELO: int = 1500
    DEDUP_TTL: str = "30d"
    TOPIC_MATCH_RESULT: str = "match.result.v1"
    TOPIC_PLAYER_UPDATED: str = "player.updated.v1"
    LOG_LEVEL: str = "INFO"
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_BACKOFF_MS: int = 100

    class Config:
        env_file = ".env"


settings = Settings()
