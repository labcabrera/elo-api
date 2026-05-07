from motor.motor_asyncio import AsyncIOMotorClient
from src.application.settings import settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGO_URI)
    return _client


def get_db():
    client = get_client()
    # If URI contains a database, get_default_database will return it; otherwise use 'elo'
    try:
        db = client.get_default_database()
    except Exception:
        db = client.get_database("elo")
    return db
