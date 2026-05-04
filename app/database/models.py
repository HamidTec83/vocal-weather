"""
models.py

Contient :
1. La structure SQL de la table (CREATE TABLE)
2. Les modèles Pydantic (validation des données)

 Objectif :
- Centraliser la structure des données
- Éviter les incohérences
"""

from typing import Literal
from pydantic import BaseModel, Field


# =========================
# Types contrôlés (validation)
# =========================

# Horizon temporel autorisé
HorizonType = Literal[
    "aujourd'hui",
    "demain",
    "semaine",
    "j+1", "j+2", "j+3", "j+4", "j+5", "j+6", "j+7"
]

# Statut de la requête
StatutType = Literal[
    "success",
    "error",
    "lieu_inconnu",
    "lieu_introuvable"
]

# Type de service STT utilisé
STTProviderType = Literal[
    "mock",
    "web_speech",
    "whisper"
]


# =========================
# SQL - création de table
# =========================

CREATE_REQUETES_TABLE = """
CREATE TABLE IF NOT EXISTS requetes (
    
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Date et heure automatique
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Texte issu de la voix
    texte_brut TEXT NOT NULL,

    -- Données extraites (NLU)
    lieu_detecte TEXT,
    horizon TEXT NOT NULL,

    -- Coordonnées GPS
    latitude REAL,
    longitude REAL,

    -- Données météo
    temp_max REAL,
    temp_min REAL,
    description TEXT,
    code_meteo INTEGER,

    -- Métadonnées
    service_stt TEXT NOT NULL,
    statut TEXT NOT NULL DEFAULT 'success'
);
"""


# =========================
# Modèles Pydantic
# =========================

class RequeteMeteoCreate(BaseModel):
    """
    Modèle utilisé lors de la création d'une requête météo.

     Sert à :
    - Valider les données AVANT insertion en base
    - Garantir des types cohérents
    """

    # Texte original issu de la voix
    texte_brut: str = Field(..., min_length=1)

    # Résultat NLU
    lieu_detecte: str | None = None
    horizon: HorizonType = "aujourd'hui"

    # Coordonnées
    latitude: float | None = None
    longitude: float | None = None

    # Résultat météo
    temp_max: float | None = None
    temp_min: float | None = None
    description: str | None = None
    code_meteo: int | None = None

    # Métadonnées
    service_stt: STTProviderType = "mock"
    statut: StatutType = "success"


class RequeteMeteoRead(RequeteMeteoCreate):
    """
    Modèle utilisé lors de la lecture depuis la base.

    👉 Hérite de RequeteMeteoCreate + ajoute :
    - id
    - timestamp
    """

    id: int
    timestamp: str