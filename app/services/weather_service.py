"""
weather_service.py

Contient toute la logique liée à la météo :

1. Transformer un nom de ville ou un code postal en coordonnées GPS
2. Appeler l'API Open-Meteo
3. Extraire les données météo d'un jour précis
4. Extraire les prévisions météo sur 7 jours
5. Transformer les codes météo WMO en descriptions lisibles
"""

import re
import requests


# =========================
# Codes météo WMO
# =========================

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
# Helpers
# =========================

def est_code_postal_francais(lieu: str) -> bool:
    """
    Vérifie si la valeur ressemble à un code postal français.

    Exemples valides :
    - 75018
    - 69003
    - 13001
    - 37000
    """

    return bool(re.fullmatch(r"\d{5}", lieu.strip()))


def obtenir_coordonnees_par_code_postal(code_postal: str) -> dict | None:
    """
    Transforme un code postal français en coordonnées GPS.

    Utilise l'API officielle geo.api.gouv.fr.

    Exemple :
    "75018" devient environ :
    {
        "nom": "Paris",
        "latitude": 48.8927,
        "longitude": 2.3487,
        "pays": "France"
    }

    Retourne None si :
    - le code postal est introuvable
    - l'API est inaccessible
    - une erreur réseau survient
    """

    url = "https://geo.api.gouv.fr/communes"

    params = {
        "codePostal": code_postal,
        "fields": "nom,centre,codesPostaux",
        "format": "json",
        "geometry": "centre",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if not data:
            return None

        commune = data[0]

        centre = commune.get("centre", {})
        coordinates = centre.get("coordinates", [])

        if len(coordinates) != 2:
            return None

        longitude = coordinates[0]
        latitude = coordinates[1]

        return {
            "nom": commune.get("nom", code_postal),
            "latitude": latitude,
            "longitude": longitude,
            "pays": "France",
        }

    except requests.RequestException as e:
        print(f"Erreur géocodage code postal : {e}")
        return None


# =========================
# Géocodage : ville/code postal -> GPS
# =========================

def obtenir_coordonnees(lieu: str) -> dict | None:
    """
    Transforme un nom de ville ou un code postal en coordonnées GPS.

    Exemples :
    "Paris" devient :
    {
        "nom": "Paris",
        "latitude": 48.8534,
        "longitude": 2.3488,
        "pays": "France"
    }

    "75018" devient :
    {
        "nom": "Paris",
        "latitude": ...,
        "longitude": ...,
        "pays": "France"
    }

    Retourne None si :
    - le lieu n'est pas trouvé
    - l'API est inaccessible
    - une erreur réseau survient
    """

    lieu = lieu.strip()

    # Si l'utilisateur donne un code postal français,
    # on utilise l'API officielle française.
    if est_code_postal_francais(lieu):
        return obtenir_coordonnees_par_code_postal(lieu)

    # Sinon, on utilise Open-Meteo pour géocoder un nom de ville.
    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": lieu,
        "count": 1,
        "language": "fr",
        "format": "json",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if not data.get("results"):
            return None

        result = data["results"][0]

        return {
            "nom": result["name"],
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "pays": result.get("country", ""),
        }

    except requests.RequestException as e:
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
    """

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "weathercode",
            "windspeed_10m_max",
        ],

        "current_weather": True,
        "timezone": "Europe/Paris",
        "forecast_days": 7,
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

    Retourne None si les données sont absentes ou invalides.
    """

    if not meteo:
        return None

    daily = meteo.get("daily", {})

    temperatures_max = daily.get("temperature_2m_max", [])
    temperatures_min = daily.get("temperature_2m_min", [])
    precipitations = daily.get("precipitation_sum", [])
    vents_max = daily.get("windspeed_10m_max", [])
    codes = daily.get("weathercode", [])

    if index < 0 or index >= len(temperatures_max):
        return None

    code = codes[index] if index < len(codes) else None

    return {
        "temp_max": temperatures_max[index],
        "temp_min": temperatures_min[index] if index < len(temperatures_min) else None,
        "precipitation": precipitations[index] if index < len(precipitations) else None,
        "vent_max": vents_max[index] if index < len(vents_max) else None,
        "code_meteo": code,
        "description": CODES_METEO.get(code, "Conditions inconnues"),
    }


# =========================
# Prévisions 7 jours
# =========================

def extraire_previsions_7_jours(meteo: dict) -> list[dict]:
    """
    Extrait les prévisions météo sur 7 jours.

    Objectif :
    fournir une liste simple exploitable par Streamlit / Plotly.
    """

    if not meteo:
        return []

    daily = meteo.get("daily", {})

    dates = daily.get("time", [])
    temperatures_max = daily.get("temperature_2m_max", [])
    temperatures_min = daily.get("temperature_2m_min", [])
    precipitations = daily.get("precipitation_sum", [])
    vents_max = daily.get("windspeed_10m_max", [])
    codes = daily.get("weathercode", [])

    previsions = []

    for index, date in enumerate(dates):
        code = codes[index] if index < len(codes) else None

        previsions.append({
            "date": date,
            "temp_max": temperatures_max[index] if index < len(temperatures_max) else None,
            "temp_min": temperatures_min[index] if index < len(temperatures_min) else None,
            "precipitation": precipitations[index] if index < len(precipitations) else None,
            "vent_max": vents_max[index] if index < len(vents_max) else None,
            "code_meteo": code,
            "description": CODES_METEO.get(code, "Conditions inconnues"),
        })

    return previsions