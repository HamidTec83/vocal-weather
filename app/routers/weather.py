"""
weather.py

Routes FastAPI liées à la météo.

Contient :
- Endpoint POST /api/v1/meteo
- Endpoint POST /api/v1/feedback
- Endpoint GET /api/v1/feedback/stats
- Pipeline texte -> NLU -> météo -> sauvegarde DB

Sécurité :
- validation stricte des entrées avec Pydantic
- rate limiting avec SlowAPI
"""

import re

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

from app.config import settings
from app.database.db import save_requete, save_feedback, get_feedback_stats
from app.database.models import RequeteMeteoCreate
from app.security.rate_limit import limiter
from app.services.nlu_service import extraire_intention, horizon_to_index
from app.services.weather_service import (
    obtenir_coordonnees,
    obtenir_meteo,
    extraire_donnees_jour,
    extraire_previsions_7_jours,
)


# Toutes les routes de ce fichier commenceront par /api/v1
router = APIRouter(prefix=settings.api_prefix)


# =========================
# Fonctions de validation
# =========================

def nettoyer_texte(texte: str) -> str:
    """
    Nettoie une chaîne utilisateur.

    Objectifs :
    - supprimer les espaces inutiles
    - éviter les entrées vides
    - limiter les caractères manifestement dangereux
    """

    texte = texte.strip()

    # Refuse certains caractères utilisés dans des injections HTML/JS simples.
    # Ce n'est pas une sécurité totale, mais c'est une bonne barrière prototype.
    if re.search(r"[<>]", texte):
        raise ValueError("Le texte contient des caractères interdits.")

    return texte


# =========================
# Modèles Pydantic
# =========================

class MeteoTexteRequest(BaseModel):
    """
    Modèle de données attendu pour l'endpoint /meteo.

    Exemple :
    {
        "texte": "Quel temps fera-t-il à Paris demain ?"
    }
    """

    texte: str = Field(
        ...,
        min_length=3,
        max_length=250,
        description="Phrase météo en langage naturel."
    )

    @field_validator("texte")
    @classmethod
    def validate_texte(cls, value: str) -> str:
        """
        Validation métier du texte météo.

        Règles :
        - pas de texte vide
        - longueur raisonnable
        - pas de caractères HTML simples < >
        """

        return nettoyer_texte(value)


class FeedbackRequest(BaseModel):
    """
    Modèle de données attendu pour l'endpoint /feedback.

    Exemple :
    {
        "requete_id": 12,
        "feedback": "up",
        "feedback_note": "Résultat correct"
    }
    """

    requete_id: int = Field(
        ...,
        ge=1,
        description="Identifiant de la requête météo."
    )

    feedback: str = Field(
        ...,
        pattern="^(up|down)$",
        description="Feedback utilisateur : up ou down."
    )

    feedback_note: str | None = Field(
        default=None,
        max_length=300,
        description="Commentaire optionnel de l'utilisateur."
    )

    @field_validator("feedback_note")
    @classmethod
    def validate_feedback_note(cls, value: str | None) -> str | None:
        """
        Valide le commentaire utilisateur optionnel.
        """

        if value is None:
            return None

        return nettoyer_texte(value)


# =========================
# Endpoint météo texte
# =========================

@router.post("/meteo")
@limiter.limit("10/minute")
def meteo_depuis_texte(request: Request, payload: MeteoTexteRequest) -> dict:
    """
    Pipeline météo complet à partir d'un texte.

    Rate limit :
    - 10 requêtes par minute par IP

    Étapes :
    1. Extraire l'intention : lieu + horizon
    2. Convertir le lieu en coordonnées GPS
    3. Récupérer la météo avec Open-Meteo
    4. Extraire le bon jour selon l'horizon
    5. Extraire les prévisions météo sur 7 jours
    6. Sauvegarder la requête en base SQLite
    7. Retourner une réponse complète au frontend
    """

    # request est nécessaire pour SlowAPI.
    # On ne l'utilise pas directement dans la logique métier.
    _ = request

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
    # 5. Prévisions sur 7 jours
    # =========================

    previsions_7_jours = extraire_previsions_7_jours(meteo)

    # =========================
    # 6. Sauvegarde en base
    # =========================

    requete_id = save_requete(RequeteMeteoCreate(
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
    # 7. Réponse API complète
    # =========================

    return {
        "statut": "ok",
        "requete_id": requete_id,
        "texte": texte,
        "lieu": coords["nom"],
        "pays": coords["pays"],
        "horizon": horizon,
        "index_jour": index_jour,
        "latitude": latitude,
        "longitude": longitude,
        "meteo": donnees_jour,
        "previsions_7_jours": previsions_7_jours,
    }


# =========================
# Endpoint feedback utilisateur
# =========================

@router.post("/feedback")
@limiter.limit("30/minute")
def feedback_utilisateur(request: Request, payload: FeedbackRequest) -> dict:
    """
    Enregistre un feedback utilisateur sur une requête météo.

    Rate limit :
    - 30 feedbacks par minute par IP

    Feedback possible :
    - "up"   : résultat utile / correct
    - "down" : résultat incorrect / insatisfaisant
    """

    _ = request

    try:
        updated = save_feedback(
            requete_id=payload.requete_id,
            feedback=payload.feedback,
            feedback_note=payload.feedback_note
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail=f"Aucune requête trouvée avec l'id {payload.requete_id}"
        )

    return {
        "statut": "ok",
        "message": "Feedback enregistré",
        "requete_id": payload.requete_id,
        "feedback": payload.feedback
    }


# =========================
# Endpoint statistiques feedback
# =========================

@router.get("/feedback/stats")
@limiter.limit("60/minute")
def feedback_stats(request: Request) -> dict:
    """
    Retourne les statistiques des feedbacks utilisateurs.

    Rate limit :
    - 60 requêtes par minute par IP
    """

    _ = request

    stats = get_feedback_stats()

    total = stats["total"]

    if total > 0:
        taux_satisfaction = round((stats["positifs"] / total) * 100, 1)
    else:
        taux_satisfaction = 0.0

    return {
        "statut": "ok",
        "stats": {
            "positifs": stats["positifs"],
            "negatifs": stats["negatifs"],
            "total": total,
            "taux_satisfaction": taux_satisfaction
        }
    }