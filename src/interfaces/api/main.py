from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.application.settings import settings
from src.interfaces.api.routers import players, leagues, matches


app = FastAPI(title="ELO Rating Service", version="0.1.0")


@app.get("/health")
async def health():
    return JSONResponse(content={"status": "ok", "env": settings.APP_ENV})


@app.get("/")
async def root():
    return {"service": "elo-api", "version": "0.1.0"}


app.include_router(players.router, prefix="/players", tags=["players"])
app.include_router(leagues.router, prefix="/leagues", tags=["leagues"])
app.include_router(matches.router, prefix="/matches", tags=["matches"])
