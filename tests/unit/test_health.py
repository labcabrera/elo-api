import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint():
    from src.interfaces.api.main import app

    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
