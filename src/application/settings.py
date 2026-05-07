from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    MONGO_URI: str
    KAFKA_BOOTSTRAP_SERVERS: str | None
    KAFKA_SCHEMA_REGISTRY: str | None
    APP_ENV: str
    DEFAULT_K_FACTOR: int
    DEFAULT_ELO: int
    DEDUP_TTL: str
    TOPIC_MATCH_RESULT: str
    TOPIC_PLAYER_UPDATED: str
    LOG_LEVEL: str
    MAX_RETRY_ATTEMPTS: int
    RETRY_BACKOFF_MS: int

    def __init__(self) -> None:
        self.MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/elo")
        self.KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
        self.KAFKA_SCHEMA_REGISTRY = os.getenv("KAFKA_SCHEMA_REGISTRY")
        self.APP_ENV = os.getenv("APP_ENV", "development")
        self.DEFAULT_K_FACTOR = int(os.getenv("DEFAULT_K_FACTOR", "32"))
        self.DEFAULT_ELO = int(os.getenv("DEFAULT_ELO", "1500"))
        self.DEDUP_TTL = os.getenv("DEDUP_TTL", "30d")
        self.TOPIC_MATCH_RESULT = os.getenv("TOPIC_MATCH_RESULT", "match.result.v1")
        self.TOPIC_PLAYER_UPDATED = os.getenv("TOPIC_PLAYER_UPDATED", "player.updated.v1")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
        self.RETRY_BACKOFF_MS = int(os.getenv("RETRY_BACKOFF_MS", "100"))


settings = Settings()
