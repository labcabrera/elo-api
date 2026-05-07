from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict


class EventPublisher(ABC):
    @abstractmethod
    async def publish_match_result(self, topic: str, payload: Dict[str, Any]) -> None:
        pass
