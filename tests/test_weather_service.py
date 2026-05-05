import pytest
import requests

from app.services.weather_service import (
    obtenir_coordonnees,
    obtenir_meteo,
    extraire_donnees_jour,
    extraire_previsions_7_jours,
)


# =========================
# Données fake réutilisables
# =========================

@pytest.fixture
def meteo_mock():
    return {
        "daily": {
            "time": [
                "2026-05-05",
                "2026-05-06",
                "2026-05-07",
            ],
            "temperature_2m_max": [20.5, 22.0, 18.3],
            "temperature_2m_min": [12.1, 13.5, 10.0],
            "precipitation_sum": [0.0, 1.2, 5.5],
            "windspeed_10m_max": [10.0, 15.5, 20.0],
            "weathercode": [0, 61, 999],
        }
    }


class FakeResponse:
    """
    Simule une réponse requests.
    """

    def __init__(self, json_data, status_error=False):
        self.json_data = json_data
        self.status_error = status_error

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_error:
            raise requests.RequestException("Erreur HTTP simulée")


# =========================
# Tests géocodage
# =========================

def test_obtenir_coordonnees_succes(monkeypatch):
    def fake_get(url, params, timeout):
        return FakeResponse({
            "results": [
                {
                    "name": "Paris",
                    "latitude": 48.8534,
                    "longitude": 2.3488,
                    "country": "France",
                }
            ]
        })

    monkeypatch.setattr(requests, "get", fake_get)

    resultat = obtenir_coordonnees("Paris")

    assert resultat == {
        "nom": "Paris",
        "latitude": 48.8534,
        "longitude": 2.3488,
        "pays": "France",
    }


def test_obtenir_coordonnees_ville_introuvable(monkeypatch):
    def fake_get(url, params, timeout):
        return FakeResponse({"results": []})

    monkeypatch.setattr(requests, "get", fake_get)

    resultat = obtenir_coordonnees("VilleInconnue")

    assert resultat is None


def test_obtenir_coordonnees_erreur_reseau(monkeypatch):
    def fake_get(url, params, timeout):
        raise requests.RequestException("Erreur réseau simulée")

    monkeypatch.setattr(requests, "get", fake_get)

    resultat = obtenir_coordonnees("Paris")

    assert resultat is None


# =========================
# Tests API météo
# =========================

def test_obtenir_meteo_succes(monkeypatch):
    fake_json = {
        "daily": {
            "temperature_2m_max": [20],
            "temperature_2m_min": [10],
            "precipitation_sum": [0],
            "windspeed_10m_max": [12],
            "weathercode": [0],
        }
    }

    def fake_get(url, params, timeout):
        assert url == "https://api.open-meteo.com/v1/forecast"
        assert params["latitude"] == 48.8534
        assert params["longitude"] == 2.3488
        assert params["forecast_days"] == 7
        assert params["timezone"] == "Europe/Paris"
        return FakeResponse(fake_json)

    monkeypatch.setattr(requests, "get", fake_get)

    resultat = obtenir_meteo(48.8534, 2.3488)

    assert resultat == fake_json


def test_obtenir_meteo_erreur_reseau(monkeypatch):
    def fake_get(url, params, timeout):
        raise requests.RequestException("Erreur météo simulée")

    monkeypatch.setattr(requests, "get", fake_get)

    resultat = obtenir_meteo(48.8534, 2.3488)

    assert resultat is None


# =========================
# Tests extraction jour
# =========================

def test_extraire_donnees_jour_aujourdhui(meteo_mock):
    resultat = extraire_donnees_jour(meteo_mock, index=0)

    assert resultat["temp_max"] == 20.5
    assert resultat["temp_min"] == 12.1
    assert resultat["precipitation"] == 0.0
    assert resultat["vent_max"] == 10.0
    assert resultat["code_meteo"] == 0
    assert resultat["description"] == "Ciel dégagé ☀️"


def test_extraire_donnees_jour_pluie(meteo_mock):
    resultat = extraire_donnees_jour(meteo_mock, index=1)

    assert resultat["temp_max"] == 22.0
    assert resultat["code_meteo"] == 61
    assert resultat["description"] == "Pluie légère 🌧️"


def test_extraire_donnees_jour_code_inconnu(meteo_mock):
    resultat = extraire_donnees_jour(meteo_mock, index=2)

    assert resultat["code_meteo"] == 999
    assert resultat["description"] == "Conditions inconnues"


def test_extraire_donnees_jour_index_invalide(meteo_mock):
    assert extraire_donnees_jour(meteo_mock, index=99) is None


def test_extraire_donnees_jour_index_negatif(meteo_mock):
    assert extraire_donnees_jour(meteo_mock, index=-1) is None


def test_extraire_donnees_jour_meteo_vide():
    assert extraire_donnees_jour(None) is None
    assert extraire_donnees_jour({}) is None


# =========================
# Tests prévisions 7 jours
# =========================

def test_extraire_previsions_7_jours(meteo_mock):
    resultat = extraire_previsions_7_jours(meteo_mock)

    assert len(resultat) == 3

    assert resultat[0]["date"] == "2026-05-05"
    assert resultat[0]["temp_max"] == 20.5
    assert resultat[0]["description"] == "Ciel dégagé ☀️"

    assert resultat[1]["date"] == "2026-05-06"
    assert resultat[1]["code_meteo"] == 61
    assert resultat[1]["description"] == "Pluie légère 🌧️"

    assert resultat[2]["date"] == "2026-05-07"
    assert resultat[2]["code_meteo"] == 999
    assert resultat[2]["description"] == "Conditions inconnues"


def test_extraire_previsions_7_jours_meteo_vide():
    assert extraire_previsions_7_jours(None) == []
    assert extraire_previsions_7_jours({}) == []


def test_extraire_previsions_7_jours_donnees_partielles():
    meteo = {
        "daily": {
            "time": ["2026-05-05", "2026-05-06"],
            "temperature_2m_max": [20.5],
            "temperature_2m_min": [],
            "precipitation_sum": [0.0, 1.2],
            "windspeed_10m_max": [],
            "weathercode": [0],
        }
    }

    resultat = extraire_previsions_7_jours(meteo)

    assert len(resultat) == 2

    assert resultat[0]["temp_max"] == 20.5
    assert resultat[0]["temp_min"] is None
    assert resultat[0]["vent_max"] is None
    assert resultat[0]["description"] == "Ciel dégagé ☀️"

    assert resultat[1]["temp_max"] is None
    assert resultat[1]["temp_min"] is None
    assert resultat[1]["code_meteo"] is None
    assert resultat[1]["description"] == "Conditions inconnues"