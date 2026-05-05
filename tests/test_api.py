from fastapi.testclient import TestClient

from app.main import app
from app.routers import weather as weather_router


client = TestClient(app)


# =========================
# GET /health
# =========================

def test_health_check():
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()
    assert data["statut"] == "ok"
    assert "app_name" in data
    assert "version" in data
    assert "env" in data


# =========================
# POST /meteo - succès
# =========================

def test_meteo_success(monkeypatch):
    monkeypatch.setattr(
        weather_router,
        "extraire_intention",
        lambda texte: {"lieu": "Paris", "horizon": "demain"}
    )

    monkeypatch.setattr(
        weather_router,
        "obtenir_coordonnees",
        lambda lieu: {
            "nom": "Paris",
            "latitude": 48.8534,
            "longitude": 2.3488,
            "pays": "France",
        }
    )

    monkeypatch.setattr(
        weather_router,
        "obtenir_meteo",
        lambda latitude, longitude: {"fake": "meteo"}
    )

    monkeypatch.setattr(
        weather_router,
        "horizon_to_index",
        lambda horizon: 1
    )

    monkeypatch.setattr(
        weather_router,
        "extraire_donnees_jour",
        lambda meteo, index: {
            "temp_max": 22.0,
            "temp_min": 12.0,
            "precipitation": 0.0,
            "vent_max": 10.0,
            "code_meteo": 0,
            "description": "Ciel dégagé ☀️",
        }
    )

    monkeypatch.setattr(
        weather_router,
        "extraire_previsions_7_jours",
        lambda meteo: []
    )

    monkeypatch.setattr(
        weather_router,
        "save_requete",
        lambda requete: 123
    )

    response = client.post(
        "/api/v1/meteo",
        json={"texte": "Quel temps fera-t-il à Paris demain ?"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["statut"] == "ok"
    assert data["requete_id"] == 123
    assert data["lieu"] == "Paris"
    assert data["pays"] == "France"
    assert data["horizon"] == "demain"
    assert data["index_jour"] == 1
    assert data["meteo"]["temp_max"] == 22.0


# =========================
# POST /meteo - lieu absent
# =========================

def test_meteo_lieu_absent(monkeypatch):
    monkeypatch.setattr(
        weather_router,
        "extraire_intention",
        lambda texte: {"lieu": None, "horizon": "demain"}
    )

    monkeypatch.setattr(
        weather_router,
        "save_requete",
        lambda requete: 1
    )

    response = client.post(
        "/api/v1/meteo",
        json={"texte": "Quel temps fera-t-il demain ?"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Aucun lieu détecté dans la phrase."


# =========================
# POST /meteo - lieu introuvable
# =========================

def test_meteo_lieu_introuvable(monkeypatch):
    monkeypatch.setattr(
        weather_router,
        "extraire_intention",
        lambda texte: {"lieu": "VilleInconnue", "horizon": "demain"}
    )

    monkeypatch.setattr(
        weather_router,
        "obtenir_coordonnees",
        lambda lieu: None
    )

    monkeypatch.setattr(
        weather_router,
        "save_requete",
        lambda requete: 1
    )

    response = client.post(
        "/api/v1/meteo",
        json={"texte": "Météo à VilleInconnue demain"}
    )

    assert response.status_code == 404
    assert "Lieu introuvable" in response.json()["detail"]


# =========================
# POST /meteo - API météo en erreur
# =========================

def test_meteo_api_meteo_erreur(monkeypatch):
    monkeypatch.setattr(
        weather_router,
        "extraire_intention",
        lambda texte: {"lieu": "Paris", "horizon": "demain"}
    )

    monkeypatch.setattr(
        weather_router,
        "obtenir_coordonnees",
        lambda lieu: {
            "nom": "Paris",
            "latitude": 48.8534,
            "longitude": 2.3488,
            "pays": "France",
        }
    )

    monkeypatch.setattr(
        weather_router,
        "obtenir_meteo",
        lambda latitude, longitude: None
    )

    monkeypatch.setattr(
        weather_router,
        "save_requete",
        lambda requete: 1
    )

    response = client.post(
        "/api/v1/meteo",
        json={"texte": "Météo à Paris demain"}
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Erreur lors de l'appel à l'API météo."


# =========================
# POST /meteo - validation Pydantic
# =========================

def test_meteo_texte_trop_court():
    response = client.post(
        "/api/v1/meteo",
        json={"texte": "ok"}
    )

    assert response.status_code == 422


def test_meteo_texte_caracteres_interdits():
    response = client.post(
        "/api/v1/meteo",
        json={"texte": "<script>alert('xss')</script>"}
    )

    assert response.status_code == 422


# =========================
# POST /feedback
# =========================

def test_feedback_success(monkeypatch):
    monkeypatch.setattr(
        weather_router,
        "save_feedback",
        lambda requete_id, feedback, feedback_note: True
    )

    response = client.post(
        "/api/v1/feedback",
        json={
            "requete_id": 1,
            "feedback": "up",
            "feedback_note": "Très utile",
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert data["statut"] == "ok"
    assert data["requete_id"] == 1
    assert data["feedback"] == "up"


def test_feedback_requete_introuvable(monkeypatch):
    monkeypatch.setattr(
        weather_router,
        "save_feedback",
        lambda requete_id, feedback, feedback_note: False
    )

    response = client.post(
        "/api/v1/feedback",
        json={
            "requete_id": 999,
            "feedback": "down",
            "feedback_note": "Pas correct",
        }
    )

    assert response.status_code == 404
    assert "Aucune requête trouvée" in response.json()["detail"]


def test_feedback_valeur_invalide():
    response = client.post(
        "/api/v1/feedback",
        json={
            "requete_id": 1,
            "feedback": "bad",
        }
    )

    assert response.status_code == 422


# =========================
# GET /feedback/stats
# =========================

def test_feedback_stats(monkeypatch):
    monkeypatch.setattr(
        weather_router,
        "get_feedback_stats",
        lambda: {
            "positifs": 8,
            "negatifs": 2,
            "total": 10,
        }
    )

    response = client.get("/api/v1/feedback/stats")

    assert response.status_code == 200

    data = response.json()
    assert data["statut"] == "ok"
    assert data["stats"]["positifs"] == 8
    assert data["stats"]["negatifs"] == 2
    assert data["stats"]["total"] == 10
    assert data["stats"]["taux_satisfaction"] == 80.0


def test_feedback_stats_vide(monkeypatch):
    monkeypatch.setattr(
        weather_router,
        "get_feedback_stats",
        lambda: {
            "positifs": 0,
            "negatifs": 0,
            "total": 0,
        }
    )

    response = client.get("/api/v1/feedback/stats")

    assert response.status_code == 200
    assert response.json()["stats"]["taux_satisfaction"] == 0.0