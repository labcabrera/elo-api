# ELO API

Minimal Python API built with FastAPI.

## Run locally

```bash
pip install -e .[dev]
uvicorn app.main:app --reload
```

## Endpoints

- `GET /` - basic API metadata
- `GET /health` - health check
- `GET /docs` - interactive Swagger UI
