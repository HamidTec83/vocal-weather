import sqlite3

import pytest

from app.database import db
from app.database.models import RequeteMeteoCreate


@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    """
    Crée une base SQLite temporaire pour les tests.

    Important :
    - ne touche jamais à la vraie base du projet
    - isole chaque test
    """
    test_db_path = tmp_path / "test_vocal_weather.db"

    monkeypatch.setattr(db, "DB_PATH", test_db_path)

    db.init_db()

    return test_db_path


def creer_requete(
    texte="Météo à Paris demain",
    lieu="Paris",
    horizon="demain",
    statut="success",
):
    return RequeteMeteoCreate(
        texte_brut=texte,
        lieu_detecte=lieu,
        horizon=horizon,
        latitude=48.8534,
        longitude=2.3488,
        temp_max=22.0,
        temp_min=12.0,
        description="Ciel dégagé ☀️",
        code_meteo=0,
        service_stt="web_speech",
        statut=statut,
    )


# =========================
# init_db
# =========================

def test_init_db_cree_table_requetes(temp_db):
    with sqlite3.connect(temp_db) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()

    noms_tables = [table[0] for table in tables]

    assert "requetes" in noms_tables


def test_init_db_ajoute_colonnes_feedback(temp_db):
    with sqlite3.connect(temp_db) as conn:
        colonnes = conn.execute(
            "PRAGMA table_info(requetes)"
        ).fetchall()

    noms_colonnes = [colonne[1] for colonne in colonnes]

    assert "feedback" in noms_colonnes
    assert "feedback_note" in noms_colonnes


# =========================
# save_requete
# =========================

def test_save_requete_insere_et_retourne_id(temp_db):
    requete = creer_requete()

    requete_id = db.save_requete(requete)

    assert isinstance(requete_id, int)
    assert requete_id >= 1

    historique = db.get_historique()

    assert len(historique) == 1
    assert historique[0]["id"] == requete_id
    assert historique[0]["texte_brut"] == "Météo à Paris demain"
    assert historique[0]["lieu_detecte"] == "Paris"
    assert historique[0]["horizon"] == "demain"
    assert historique[0]["statut"] == "success"


# =========================
# get_historique
# =========================

def test_get_historique_respecte_limit(temp_db):
    db.save_requete(creer_requete(texte="Météo à Paris demain", lieu="Paris"))
    db.save_requete(creer_requete(texte="Météo à Lyon demain", lieu="Lyon"))
    db.save_requete(creer_requete(texte="Météo à Lille demain", lieu="Lille"))

    historique = db.get_historique(limit=2)

    assert len(historique) == 2


def test_get_historique_base_vide(temp_db):
    historique = db.get_historique()

    assert historique == []


# =========================
# save_feedback
# =========================

def test_save_feedback_success(temp_db):
    requete_id = db.save_requete(creer_requete())

    updated = db.save_feedback(
        requete_id=requete_id,
        feedback="up",
        feedback_note="Réponse correcte",
    )

    assert updated is True

    historique = db.get_historique()

    assert historique[0]["feedback"] == "up"
    assert historique[0]["feedback_note"] == "Réponse correcte"


def test_save_feedback_requete_introuvable(temp_db):
    updated = db.save_feedback(
        requete_id=999,
        feedback="up",
        feedback_note="id inexistant",
    )

    assert updated is False


def test_save_feedback_valeur_invalide(temp_db):
    requete_id = db.save_requete(creer_requete())

    with pytest.raises(ValueError) as erreur:
        db.save_feedback(
            requete_id=requete_id,
            feedback="bad",
            feedback_note=None,
        )

    assert "up" in str(erreur.value)
    assert "down" in str(erreur.value)


# =========================
# get_feedback_stats
# =========================

def test_get_feedback_stats_base_vide(temp_db):
    stats = db.get_feedback_stats()

    assert stats == {
        "positifs": 0,
        "negatifs": 0,
        "total": 0,
    }


def test_get_feedback_stats(temp_db):
    id_1 = db.save_requete(creer_requete(texte="Météo Paris", lieu="Paris"))
    id_2 = db.save_requete(creer_requete(texte="Météo Lyon", lieu="Lyon"))
    id_3 = db.save_requete(creer_requete(texte="Météo Lille", lieu="Lille"))

    db.save_feedback(id_1, "up")
    db.save_feedback(id_2, "up")
    db.save_feedback(id_3, "down")

    stats = db.get_feedback_stats()

    assert stats["positifs"] == 2
    assert stats["negatifs"] == 1
    assert stats["total"] == 3