from typing import Any, Dict, List, Optional
from uuid import uuid4
from datetime import datetime
from src.infrastructure.persistence.mongo import get_db
from src.application.ports.repository import PlayerRepository

db = get_db()


class MongoPlayerRepository(PlayerRepository):
    def __init__(self):
        self._col = db.players

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pid = str(uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        doc = {
            "_id": pid,
            "id_external": data.get("id_external"),
            "name": data.get("name"),
            "league_id": str(data.get("league_id")),
            "elo": float(data.get("elo", 1500)),
            "version": 1,
            "metadata": data.get("metadata", {}),
            "created_at": now,
            "updated_at": now,
        }
        await self._col.insert_one(doc)
        return doc

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        return await self._col.find_one({"_id": id})

    async def list(self, filter: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        cursor = self._col.find(filter or {})
        return await cursor.to_list(length=1000)

    async def update(self, id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates["updated_at"] = datetime.utcnow().isoformat() + "Z"
        await self._col.update_one({"_id": id}, {"$set": updates, "$inc": {"version": 1}})
        return await self.get_by_id(id)

    async def update_with_version(self, id: str, expected_version: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Attempt to update document only if version matches; returns updated doc or None on conflict."""
        updates["updated_at"] = datetime.utcnow().isoformat() + "Z"
        result = await self._col.update_one({"_id": id, "version": expected_version}, {"$set": updates, "$inc": {"version": 1}})
        if result.modified_count == 0:
            return None
        return await self.get_by_id(id)

    async def delete(self, id: str) -> None:
        await self._col.delete_one({"_id": id})


player_repository = MongoPlayerRepository()
