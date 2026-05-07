from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_returns_api_metadata() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "ELO API",
        "framework": "FastAPI",
        "language": "Python",
    }


def test_health_check_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_metadata_uses_elo_api_title() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "ELO API"
