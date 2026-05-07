from typing import Dict, Any
from src.application.ports.messaging import EventPublisher
import asyncio
import logging

logger = logging.getLogger(__name__)


class ConsolePublisher(EventPublisher):
    async def publish_match_result(self, topic: str, payload: Dict[str, Any]) -> None:
        # Simple non-blocking log-based publisher for scaffolding
        logger.info("Publishing to %s: %s", topic, payload)
        # simulate async IO
        await asyncio.sleep(0)


publisher = ConsolePublisher()
