"""
db.py

Contient :
- Connexion à SQLite
- Initialisation de la base
- Migration simple de la base existante
- Gestion propre des connexions
- Fonctions d'écriture et de lecture

Objectif :
- Isoler toute la logique liée à SQLite
- Éviter de mélanger SQL et logique métier dans les routers/services
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager

from app.config import settings
from app.database.models import CREATE_REQUETES_TABLE, RequeteMeteoCreate


# =========================
# Chemin de la base
# =========================

# Exemple :
# settings.db_path = "data/vocal_weather.db"
DB_PATH = Path(settings.db_path)


# =========================
# Initialisation / migration
# =========================

def init_db() -> None:
    """
    Initialise la base SQLite.

    Actions :
    1. Crée le dossier data/ si nécessaire
    2. Crée la table requetes si elle n'existe pas
    3. Ajoute les colonnes de feedback si elles n'existent pas encore

    Pourquoi une migration ?
    - La table existe déjà dans ton projet
    - On veut ajouter feedback / feedback_note sans supprimer les anciennes données
    """

    # Crée le dossier parent de la base si nécessaire
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        # Création initiale de la table
        conn.execute(CREATE_REQUETES_TABLE)

        # Ajout automatique des colonnes feedback si absentes
        _add_column_if_not_exists(
            conn=conn,
            table_name="requetes",
            column_name="feedback",
            column_definition="TEXT"
        )

        _add_column_if_not_exists(
            conn=conn,
            table_name="requetes",
            column_name="feedback_note",
            column_definition="TEXT"
        )

        conn.commit()


def _add_column_if_not_exists(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str,
    column_definition: str
) -> None:
    """
    Ajoute une colonne à une table SQLite seulement si elle n'existe pas.

    Exemple :
    _add_column_if_not_exists(
        conn,
        "requetes",
        "feedback",
        "TEXT"
    )

    Pourquoi ?
    SQLite ne supporte pas directement :
    ALTER TABLE ADD COLUMN IF NOT EXISTS
    """

    # PRAGMA table_info retourne les colonnes existantes
    existing_columns = conn.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    existing_column_names = [column[1] for column in existing_columns]

    if column_name not in existing_column_names:
        conn.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        )


# =========================
# Gestion des connexions
# =========================

@contextmanager
def get_connection():
    """
    Fournit une connexion SQLite propre.

    Avantages :
    - fermeture automatique
    - utilisable avec "with"
    - accès aux colonnes par nom grâce à sqlite3.Row

    Exemple :
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM requetes").fetchall()
    """

    conn = sqlite3.connect(DB_PATH)

    # Permet :
    # row["texte_brut"] au lieu de row[0]
    conn.row_factory = sqlite3.Row

    try:
        yield conn
    finally:
        conn.close()


# =========================
# Écriture en base
# =========================

def save_requete(data: RequeteMeteoCreate) -> int:
    """
    Insère une requête météo dans la table requetes.

    Retourne :
    - l'id de la ligne créée

    Pourquoi retourner l'id ?
    - Cela permet au frontend d'envoyer ensuite un feedback 👍/👎
      associé à cette requête précise.
    """

    with get_connection() as conn:
        cursor = conn.execute("""
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

        # ID auto-incrémenté créé par SQLite
        return cursor.lastrowid


def save_feedback(
    requete_id: int,
    feedback: str,
    feedback_note: str | None = None
) -> bool:
    """
    Enregistre un feedback utilisateur sur une requête météo.

    Paramètres :
    - requete_id : id de la requête météo
    - feedback : "up" ou "down"
    - feedback_note : commentaire optionnel

    Retourne :
    - True si une ligne a été modifiée
    - False si aucun id correspondant n'a été trouvé
    """

    if feedback not in {"up", "down"}:
        raise ValueError("Le feedback doit être 'up' ou 'down'.")

    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE requetes
            SET feedback = ?,
                feedback_note = ?
            WHERE id = ?
        """, (
            feedback,
            feedback_note,
            requete_id
        ))

        conn.commit()

        return cursor.rowcount > 0


# =========================
# Lecture en base
# =========================

def get_historique(limit: int = 10) -> list[dict]:
    """
    Récupère les dernières requêtes météo.

    Retour :
    [
        {
            "id": 1,
            "timestamp": "...",
            "texte_brut": "...",
            "lieu_detecte": "...",
            "feedback": "up",
            ...
        }
    ]
    """

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT *
            FROM requetes
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [dict(row) for row in rows]


def get_feedback_stats() -> dict:
    """
    Retourne des statistiques simples sur les feedbacks.

    Exemple :
    {
        "positifs": 8,
        "negatifs": 2,
        "total": 10
    }

    Cette fonction sera utile plus tard pour un dashboard de monitoring.
    """

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT feedback, COUNT(*) as count
            FROM requetes
            WHERE feedback IS NOT NULL
            GROUP BY feedback
        """).fetchall()

        stats = {
            "positifs": 0,
            "negatifs": 0,
            "total": 0
        }

        for row in rows:
            if row["feedback"] == "up":
                stats["positifs"] = row["count"]
            elif row["feedback"] == "down":
                stats["negatifs"] = row["count"]

        stats["total"] = stats["positifs"] + stats["negatifs"]

        return stats