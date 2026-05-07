from typing import Any, Dict, List, Optional
from uuid import uuid4
from datetime import datetime
from src.infrastructure.persistence.mongo import get_db
from src.application.ports.repository import LeagueRepository

db = get_db()


class MongoLeagueRepository(LeagueRepository):
    def __init__(self):
        self._col = db.leagues

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        lid = str(uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        doc = {
            "_id": lid,
            "name": data.get("name"),
            "k_factor": float(data.get("k_factor", 32)),
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
        await self._col.update_one({"_id": id}, {"$set": updates})
        return await self.get_by_id(id)

    async def delete(self, id: str) -> None:
        await self._col.delete_one({"_id": id})


league_repository = MongoLeagueRepository()
