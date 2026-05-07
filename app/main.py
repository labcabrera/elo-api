from fastapi import FastAPI

app = FastAPI(title="ELO API", version="0.1.0")


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "name": "ELO API",
        "framework": "FastAPI",
        "language": "Python",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
