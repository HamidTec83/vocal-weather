"""
voice.py

Routes liées à la voix (audio).

Objectifs :
- Recevoir un fichier audio
- Le transcrire (STT)
- Lancer le pipeline météo complet
"""

import os
import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import settings
from app.services.stt_service import transcrire_audio
from app.services.nlu_service import extraire_intention, horizon_to_index
from app.services.weather_service import (
    obtenir_coordonnees,
    obtenir_meteo,
    extraire_donnees_jour
)
from app.database.db import save_requete
from app.database.models import RequeteMeteoCreate


router = APIRouter(prefix=settings.api_prefix)


# =========================
# 1. Transcription seule
# =========================

@router.post("/transcrire")
def transcrire(fichier: UploadFile = File(...)):
    """
    Endpoint simple :
    audio → texte
    """

    try:
        # Sauvegarde temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(fichier.file.read())
            tmp_path = tmp.name

        texte = transcrire_audio(tmp_path)

        return {"texte": texte}

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# =========================
# 2. Pipeline complet
# =========================

@router.post("/meteo-vocale")
def meteo_vocale(fichier: UploadFile = File(...)):
    """
    Pipeline complet :
    audio → texte → NLU → météo → DB
    """

    try:
        # 1. Sauvegarde temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(fichier.file.read())
            tmp_path = tmp.name

        # 2. STT
        texte = transcrire_audio(tmp_path)

        # 3. NLU
        intention = extraire_intention(texte)
        lieu = intention["lieu"]
        horizon = intention["horizon"]

        if not lieu:
            raise HTTPException(400, "Lieu non détecté")

        # 4. Géocodage
        coords = obtenir_coordonnees(lieu)
        if not coords:
            raise HTTPException(404, f"Lieu introuvable : {lieu}")

        # 5. Météo
        meteo = obtenir_meteo(coords["latitude"], coords["longitude"])
        if not meteo:
            raise HTTPException(502, "Erreur API météo")

        # 6. Extraction jour
        index = horizon_to_index(horizon)
        resume = extraire_donnees_jour(meteo, index)

        # 7. Sauvegarde
        save_requete(RequeteMeteoCreate(
            texte_brut=texte,
            lieu_detecte=coords["nom"],
            horizon=horizon,
            latitude=coords["latitude"],
            longitude=coords["longitude"],
            temp_max=resume["temp_max"],
            temp_min=resume["temp_min"],
            description=resume["description"],
            code_meteo=resume["code_meteo"],
            service_stt=settings.stt_provider,
            statut="success"
        ))

        return {
            "statut": "ok",
            "texte": texte,
            "lieu": coords["nom"],
            "horizon": horizon,
            "meteo": resume
        }

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)