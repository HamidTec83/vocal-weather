"""
weather.py

Routes FastAPI liées à la météo.

Contient :
- Endpoint POST /api/v1/meteo
- Pipeline texte -> NLU -> météo -> sauvegarde DB
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import settings
from app.database.db import save_requete
from app.database.models import RequeteMeteoCreate
from app.services.nlu_service import extraire_intention, horizon_to_index
from app.services.weather_service import (
    obtenir_coordonnees,
    obtenir_meteo,
    extraire_donnees_jour,
)


# Router dédié aux routes météo.
# Toutes les routes de ce fichier commenceront par /api/v1
router = APIRouter(prefix=settings.api_prefix)


class MeteoTexteRequest(BaseModel):
    """
    Modèle de données attendu dans le body JSON.

    Exemple :
    {
        "texte": "Quel temps fera-t-il à Paris demain ?"
    }
    """

    texte: str = Field(..., min_length=1)


@router.post("/meteo")
def meteo_depuis_texte(payload: MeteoTexteRequest) -> dict:
    """
    Pipeline météo complet à partir d'un texte.

    Étapes :
    1. Extraire l'intention : lieu + horizon
    2. Convertir le lieu en coordonnées GPS
    3. Récupérer la météo avec Open-Meteo
    4. Extraire le bon jour selon l'horizon
    5. Sauvegarder la requête en base SQLite
    6. Retourner une réponse complète au frontend
    """

    texte = payload.texte

    # =========================
    # 1. NLU : lieu + horizon
    # =========================

    intention = extraire_intention(texte)
    lieu = intention["lieu"]
    horizon = intention["horizon"]

    if not lieu:
        save_requete(RequeteMeteoCreate(
            texte_brut=texte,
            lieu_detecte=None,
            horizon=horizon,
            service_stt="web_speech",
            statut="lieu_inconnu"
        ))

        raise HTTPException(
            status_code=400,
            detail="Aucun lieu détecté dans la phrase."
        )

    # =========================
    # 2. Géocodage
    # =========================

    coords = obtenir_coordonnees(lieu)

    if not coords:
        save_requete(RequeteMeteoCreate(
            texte_brut=texte,
            lieu_detecte=lieu,
            horizon=horizon,
            service_stt="web_speech",
            statut="lieu_introuvable"
        ))

        raise HTTPException(
            status_code=404,
            detail=f"Lieu introuvable : {lieu}"
        )

    latitude = coords["latitude"]
    longitude = coords["longitude"]

    # =========================
    # 3. Appel API météo
    # =========================

    meteo = obtenir_meteo(latitude, longitude)

    if not meteo:
        save_requete(RequeteMeteoCreate(
            texte_brut=texte,
            lieu_detecte=coords["nom"],
            horizon=horizon,
            latitude=latitude,
            longitude=longitude,
            service_stt="web_speech",
            statut="error"
        ))

        raise HTTPException(
            status_code=502,
            detail="Erreur lors de l'appel à l'API météo."
        )

    # =========================
    # 4. Extraction du bon jour
    # =========================

    index_jour = horizon_to_index(horizon)

    donnees_jour = extraire_donnees_jour(
        meteo=meteo,
        index=index_jour
    )

    if not donnees_jour:
        raise HTTPException(
            status_code=500,
            detail="Impossible d'extraire les données météo du jour demandé."
        )

    # =========================
    # 5. Sauvegarde en base
    # =========================

    save_requete(RequeteMeteoCreate(
        texte_brut=texte,
        lieu_detecte=coords["nom"],
        horizon=horizon,
        latitude=latitude,
        longitude=longitude,
        temp_max=donnees_jour["temp_max"],
        temp_min=donnees_jour["temp_min"],
        description=donnees_jour["description"],
        code_meteo=donnees_jour["code_meteo"],
        service_stt="web_speech",
        statut="success"
    ))

    # =========================
    # 6. Réponse API complète
    # =========================

    return {
        "statut": "ok",
        "texte": texte,
        "lieu": coords["nom"],
        "pays": coords["pays"],
        "horizon": horizon,
        "index_jour": index_jour,

        # Important pour la carte Streamlit
        "latitude": latitude,
        "longitude": longitude,

        "meteo": donnees_jour
    }