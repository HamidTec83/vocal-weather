from fastapi.testclient import TestClient
from app.main import app
from app.routers import voice as voice_router

import io

client = TestClient(app)


# =========================
# POST /transcrire
# =========================

def test_transcrire(monkeypatch):
    monkeypatch.setattr(
        voice_router,
        "transcrire_audio",
        lambda path: "Météo à Paris demain"
    )

    file = {"fichier": ("audio.wav", io.BytesIO(b"fake"), "audio/wav")}

    response = client.post("/api/v1/transcrire", files=file)

    assert response.status_code == 200
    assert response.json()["texte"] == "Météo à Paris demain"


# =========================
# POST /meteo-vocale success
# =========================

def test_meteo_vocale_success(monkeypatch):
    monkeypatch.setattr(
        voice_router,
        "transcrire_audio",
        lambda path: "Météo à Paris demain"
    )

    monkeypatch.setattr(
        voice_router,
        "extraire_intention",
        lambda texte: {"lieu": "Paris", "horizon": "demain"}
    )

    monkeypatch.setattr(
        voice_router,
        "obtenir_coordonnees",
        lambda lieu: {
            "nom": "Paris",
            "latitude": 48.85,
            "longitude": 2.35,
        }
    )

    monkeypatch.setattr(
        voice_router,
        "obtenir_meteo",
        lambda lat, lon: {"fake": "meteo"}
    )

    monkeypatch.setattr(
        voice_router,
        "horizon_to_index",
        lambda h: 1
    )

    monkeypatch.setattr(
        voice_router,
        "extraire_donnees_jour",
        lambda m, i: {
            "temp_max": 20,
            "temp_min": 10,
            "description": "Ciel dégagé ☀️",
            "code_meteo": 0
        }
    )

    monkeypatch.setattr(
        voice_router,
        "save_requete",
        lambda r: 1
    )

    file = {"fichier": ("audio.wav", io.BytesIO(b"fake"), "audio/wav")}

    response = client.post("/api/v1/meteo-vocale", files=file)

    assert response.status_code == 200
    assert response.json()["statut"] == "ok"
    assert response.json()["lieu"] == "Paris"


# =========================
# erreur : lieu non détecté
# =========================

def test_meteo_vocale_lieu_absent(monkeypatch):
    monkeypatch.setattr(
        voice_router,
        "transcrire_audio",
        lambda path: "blabla"
    )

    monkeypatch.setattr(
        voice_router,
        "extraire_intention",
        lambda texte: {"lieu": None, "horizon": "demain"}
    )

    file = {"fichier": ("audio.wav", io.BytesIO(b"fake"), "audio/wav")}

    response = client.post("/api/v1/meteo-vocale", files=file)

    assert response.status_code == 400


# =========================
# erreur : lieu introuvable
# =========================

def test_meteo_vocale_lieu_introuvable(monkeypatch):
    monkeypatch.setattr(
        voice_router,
        "transcrire_audio",
        lambda path: "Météo à X demain"
    )

    monkeypatch.setattr(
        voice_router,
        "extraire_intention",
        lambda texte: {"lieu": "X", "horizon": "demain"}
    )

    monkeypatch.setattr(
        voice_router,
        "obtenir_coordonnees",
        lambda lieu: None
    )

    file = {"fichier": ("audio.wav", io.BytesIO(b"fake"), "audio/wav")}

    response = client.post("/api/v1/meteo-vocale", files=file)

    assert response.status_code == 404