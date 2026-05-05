"""
main.py

Point d'entrée principal de l'application FastAPI.

Contient :
- Création de l'application FastAPI
- Initialisation SQLite au démarrage
- Ajout des routers
- Sécurité API : rate limiting + headers HTTP
"""

from fastapi import FastAPI, Request

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.database.db import init_db, get_historique
from app.routers.weather import router as weather_router
from app.routers.voice import router as voice_router
from app.security.headers import SecurityHeadersMiddleware
from app.security.rate_limit import limiter


# =========================
# Création de l'application
# =========================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API backend du projet Vocal Weather"
)


# =========================
# Sécurité API
# =========================

# Active SlowAPI sur l'application
app.state.limiter = limiter

# Gestion propre des erreurs 429 Too Many Requests
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

# Middleware SlowAPI
app.add_middleware(SlowAPIMiddleware)

# Headers de sécurité HTTP
app.add_middleware(SecurityHeadersMiddleware)


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
    """
    Initialise la base SQLite au démarrage.
    """

    init_db()


# =========================
# Endpoint santé
# =========================

@app.get(f"{settings.api_prefix}/health")
@limiter.limit("30/minute")
def health_check(request: Request) -> dict:
    """
    Vérifie que l'API fonctionne.

    Rate limit :
    - 30 requêtes par minute par IP
    """

    _ = request

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
@limiter.limit("20/minute")
def historique(request: Request, limit: int = 10) -> dict:
    """
    Retourne les dernières requêtes météo sauvegardées.

    Rate limit :
    - 20 requêtes par minute par IP
    """

    _ = request

    return {
        "historique": get_historique(limit)
    }