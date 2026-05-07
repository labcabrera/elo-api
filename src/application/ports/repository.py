from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class PlayerRepository(ABC):
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def list(self, filter: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def update(self, id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def delete(self, id: str) -> None:
        pass


class LeagueRepository(ABC):
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def list(self, filter: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def update(self, id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def delete(self, id: str) -> None:
        pass


class MatchRepository(ABC):
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_by_external_id(self, external_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        pass
