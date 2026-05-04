"""
stt_service.py

STT = Speech To Text

Objectif :
- Recevoir un fichier audio
- Le transcrire en texte
- Utiliser OpenAI Whisper si une clé API est disponible
- Utiliser un mode mock si on veut tester sans clé
"""

from openai import OpenAI

from app.config import settings


def transcrire_audio(chemin_fichier: str) -> str:
    """
    Transcrit un fichier audio en texte.

    Paramètre :
    - chemin_fichier : chemin local vers le fichier audio

    Retour :
    - texte transcrit
    """

    # Mode mock : utile pour tester sans clé OpenAI
    if settings.stt_provider == "mock":
        return "Quel temps fera-t-il à Paris demain ?"

    # Sécurité : si Whisper est demandé mais sans clé API
    if settings.stt_provider == "whisper" and not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY manquante dans le fichier .env")

    # Client OpenAI
    client = OpenAI(api_key=settings.openai_api_key)

    # Ouverture du fichier audio en binaire
    with open(chemin_fichier, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="fr"
        )

    return transcription.text