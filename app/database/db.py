"""
db.py

Contient :
- Connexion à SQLite
- Initialisation de la base
- Gestion propre des connexions
- Fonctions d'écriture et de lecture

Objectif :
- Isoler toute la logique base de données
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager

from app.config import settings
from app.database.models import CREATE_REQUETES_TABLE, RequeteMeteoCreate


# =========================
# Chemin de la base
# =========================

DB_PATH = Path(settings.db_path)


# =========================
# Initialisation de la base
# =========================

def init_db() -> None:
    """
    Initialise la base SQLite.

    Actions :
    1. Crée le dossier /data si nécessaire
    2. Crée la table 'requetes' si elle n'existe pas
    """

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(CREATE_REQUETES_TABLE)
        conn.commit()


# =========================
# Gestion des connexions
# =========================

@contextmanager
def get_connection():
    """
    Fournit une connexion SQLite propre.

    Avantages :
    - Fermeture automatique
    - Utilisable avec "with"
    - Accès aux colonnes par nom grâce à sqlite3.Row
    """

    conn = sqlite3.connect(DB_PATH)

    # Permet : row["texte_brut"] au lieu de row[0]
    conn.row_factory = sqlite3.Row

    try:
        yield conn
    finally:
        conn.close()


# =========================
# Écriture en base
# =========================

def save_requete(data: RequeteMeteoCreate) -> None:
    """
    Insère une requête météo dans la table 'requetes'.
    """

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO requetes (
                texte_brut,
                lieu_detecte,
                horizon,
                latitude,
                longitude,
                temp_max,
                temp_min,
                description,
                code_meteo,
                service_stt,
                statut
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.texte_brut,
            data.lieu_detecte,
            data.horizon,
            data.latitude,
            data.longitude,
            data.temp_max,
            data.temp_min,
            data.description,
            data.code_meteo,
            data.service_stt,
            data.statut
        ))

        conn.commit()


# =========================
# Lecture en base
# =========================

def get_historique(limit: int = 10) -> list[dict]:
    """
    Récupère les dernières requêtes météo.
    """

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT *
            FROM requetes
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [dict(row) for row in rows]