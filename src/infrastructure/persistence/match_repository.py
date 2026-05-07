from typing import Any, Dict, Optional
from uuid import uuid4
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from src.infrastructure.persistence.mongo import get_db
from src.application.ports.repository import MatchRepository

db = get_db()


class MongoMatchRepository(MatchRepository):
    def __init__(self):
        self._col = db.matches

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        mid = str(uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        doc = {
            "_id": mid,
            "external_match_id": data.get("external_match_id"),
            "league_id": str(data.get("league_id")),
            "player_a_id": str(data.get("player_a_id")),
            "player_b_id": str(data.get("player_b_id")),
            "winner_id": str(data.get("winner_id")) if data.get("winner_id") else None,
            "score": data.get("score"),
            "timestamp": data.get("timestamp") or now,
            "elo_before": data.get("elo_before"),
            "elo_after": data.get("elo_after"),
            "created_at": now,
        }
        try:
            await self._col.insert_one(doc)
            return doc
        except DuplicateKeyError:
            # If there's a duplicate external_match_id, return existing doc
            if data.get("external_match_id"):
                existing = await self.get_by_external_id(data.get("external_match_id"))
                if existing:
                    return existing
            raise

    async def get_by_external_id(self, external_id: str) -> Optional[Dict[str, Any]]:
        return await self._col.find_one({"external_match_id": external_id})

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        return await self._col.find_one({"_id": id})


match_repository = MongoMatchRepository()
