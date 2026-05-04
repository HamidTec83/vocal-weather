from fastapi import FastAPI

from app.config import settings
from app.database.db import init_db, get_historique
from app.routers.weather import router as weather_router
from app.routers.voice import router as voice_router


# =========================
# Création de l'application
# =========================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API backend du projet Vocal Weather"
)


# =========================
# Ajout des routers
# =========================

app.include_router(weather_router)
app.include_router(voice_router)


# =========================
# Événement de démarrage
# =========================

@app.on_event("startup")
def startup_event() -> None:
    init_db()


# =========================
# Endpoint santé
# =========================

@app.get(f"{settings.api_prefix}/health")
def health_check() -> dict:
    return {
        "statut": "ok",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "env": settings.env
    }


# =========================
# Endpoint historique
# =========================

@app.get(f"{settings.api_prefix}/historique")
def historique(limit: int = 10) -> dict:
    return {
        "historique": get_historique(limit)
    }