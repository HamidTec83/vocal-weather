"""
weather_service.py

Contient toute la logique liée à la météo :

1. Transformer un nom de ville en coordonnées GPS
2. Appeler l'API Open-Meteo
3. Extraire les données utiles pour un jour précis
4. Transformer les codes météo WMO en descriptions lisibles

API utilisée :
- Géocodage : https://geocoding-api.open-meteo.com
- Météo     : https://api.open-meteo.com
"""

import requests


# =========================
# Codes météo WMO
# =========================

# Open-Meteo renvoie des codes météo numériques.
# Exemple : 0 = ciel dégagé, 61 = pluie légère.
# Ce dictionnaire permet d'afficher une description compréhensible.
CODES_METEO = {
    0: "Ciel dégagé ☀️",
    1: "Principalement dégagé 🌤️",
    2: "Partiellement nuageux ⛅",
    3: "Couvert ☁️",
    45: "Brouillard 🌫️",
    48: "Brouillard givrant 🌫️",
    51: "Bruine légère 🌦️",
    53: "Bruine modérée 🌦️",
    55: "Bruine forte 🌦️",
    61: "Pluie légère 🌧️",
    63: "Pluie modérée 🌧️",
    65: "Pluie forte 🌧️",
    71: "Neige légère ❄️",
    73: "Neige modérée ❄️",
    75: "Neige forte ❄️",
    80: "Averses légères 🌦️",
    81: "Averses modérées 🌦️",
    82: "Averses fortes 🌦️",
    95: "Orage ⛈️",
    96: "Orage avec grêle légère ⛈️",
    99: "Orage avec grêle forte ⛈️",
}


# =========================
# Géocodage : ville -> GPS
# =========================

def obtenir_coordonnees(lieu: str) -> dict | None:
    """
    Transforme un nom de ville en coordonnées GPS.

    Exemple :
    "Paris" devient :
    {
        "nom": "Paris",
        "latitude": 48.8534,
        "longitude": 2.3488,
        "pays": "France"
    }

    Retourne None si :
    - la ville n'est pas trouvée
    - l'API est inaccessible
    - une erreur réseau survient
    """

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": lieu,
        "count": 1,
        "language": "fr",
        "format": "json"
    }

    try:
        # timeout=10 évite que l'application reste bloquée trop longtemps
        response = requests.get(url, params=params, timeout=10)

        # Déclenche une erreur si le statut HTTP est 4xx ou 5xx
        response.raise_for_status()

        data = response.json()

        # Si Open-Meteo ne trouve aucune ville
        if not data.get("results"):
            return None

        result = data["results"][0]

        return {
            "nom": result["name"],
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "pays": result.get("country", "")
        }

    except requests.RequestException as e:
        # Pour un prototype, print suffit.
        # Plus tard, on pourra remplacer par logging.
        print(f"Erreur géocodage : {e}")
        return None


# =========================
# Appel API météo
# =========================

def obtenir_meteo(latitude: float, longitude: float) -> dict | None:
    """
    Récupère les prévisions météo sur 7 jours
    pour une latitude et une longitude données.

    Retourne le JSON complet de l'API Open-Meteo.

    Retourne None si :
    - l'API est inaccessible
    - une erreur HTTP survient
    - une erreur réseau survient
    """

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,

        # Données journalières nécessaires pour le projet
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "weathercode",
            "windspeed_10m_max"
        ],

        # Données météo actuelles
        "current_weather": True,

        # Fuseau horaire français
        "timezone": "Europe/Paris",

        # Prévisions sur 7 jours
        "forecast_days": 7
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        print(f"Erreur météo : {e}")
        return None


# =========================
# Extraction d'un jour précis
# =========================

def extraire_donnees_jour(meteo: dict, index: int = 0) -> dict | None:
    """
    Extrait les données météo d'un jour précis.

    index :
    - 0 = aujourd'hui
    - 1 = demain
    - 2 = après-demain
    - ...
    - 6 = dans 6 jours

    Retourne :
    {
        "temp_max": 22.4,
        "temp_min": 14.1,
        "precipitation": 0.2,
        "vent_max": 18.5,
        "code_meteo": 2,
        "description": "Partiellement nuageux ⛅"
    }

    Retourne None si :
    - meteo est vide
    - l'index demandé est invalide
    - les données journalières sont absentes
    """

    if not meteo:
        return None

    daily = meteo.get("daily", {})

    temperatures_max = daily.get("temperature_2m_max", [])
    temperatures_min = daily.get("temperature_2m_min", [])
    precipitations = daily.get("precipitation_sum", [])
    vents_max = daily.get("windspeed_10m_max", [])
    codes = daily.get("weathercode", [])

    # Sécurité : évite IndexError si l'index n'existe pas
    if index < 0 or index >= len(temperatures_max):
        return None

    code = codes[index] if index < len(codes) else None

    return {
        "temp_max": temperatures_max[index],
        "temp_min": temperatures_min[index] if index < len(temperatures_min) else None,
        "precipitation": precipitations[index] if index < len(precipitations) else None,
        "vent_max": vents_max[index] if index < len(vents_max) else None,
        "code_meteo": code,
        "description": CODES_METEO.get(code, "Conditions inconnues")
    }