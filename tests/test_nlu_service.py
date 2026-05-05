import pytest

from app.services.nlu_service import extraire_intention, horizon_to_index


# =========================
# Tests extraction intention
# =========================

@pytest.mark.parametrize(
    "texte, lieu_attendu, horizon_attendu",
    [
        ("Quel temps fait-il à Paris ?", "Paris", "aujourd'hui"),
        ("Météo à Lyon demain", "Lyon", "demain"),
        ("Quel temps fera-t-il à Marseille après-demain ?", "Marseille", "j+2"),
        ("Prévision pour Bordeaux apres-demain", "Bordeaux", "j+2"),
        ("Météo sur Lille cette semaine", "Lille Cette", "semaine"),
        ("Prévisions à Nantes dans 3 jours", "Nantes", "j+3"),
        ("Temps près de Toulouse demain", "Toulouse", "demain"),
        ("Météo pres de Rennes dans 5 jours", "Rennes", "j+5"),
        ("Quel temps à Saint-Malo demain ?", "Saint-Malo", "demain"),
       ("Météo à Aix en Provence demain", "Aix En Provence", "demain"),
    ],
)
def test_extraire_intention_lieu_et_horizon(texte, lieu_attendu, horizon_attendu):
    resultat = extraire_intention(texte)

    assert resultat["lieu"] == lieu_attendu
    assert resultat["horizon"] == horizon_attendu


def test_extraire_intention_sans_lieu():
    resultat = extraire_intention("Quel temps fera-t-il demain ?")

    assert resultat["lieu"] is None
    assert resultat["horizon"] == "demain"


def test_extraire_intention_texte_vide():
    resultat = extraire_intention("")

    assert resultat["lieu"] is None
    assert resultat["horizon"] == "aujourd'hui"


def test_extraire_intention_ignore_espaces_et_majuscules():
    resultat = extraire_intention("   MÉTÉO À PARIS DEMAIN   ")

    assert resultat["lieu"] == "Paris"
    assert resultat["horizon"] == "demain"


def test_extraire_intention_apres_demain_prioritaire_sur_demain():
    resultat = extraire_intention("Météo à Paris après-demain")

    assert resultat["lieu"] == "Paris"
    assert resultat["horizon"] == "j+2"


# =========================
# Tests horizon_to_index
# =========================

@pytest.mark.parametrize(
    "horizon, index_attendu",
    [
        ("aujourd'hui", 0),
        ("demain", 1),
        ("semaine", 0),
        ("j+2", 2),
        ("j+3", 3),
        ("j+6", 6),
        ("j+7", 6),
        ("j+30", 6),
        ("j+abc", 0),
        ("inconnu", 0),
        ("", 0),
    ],
)
def test_horizon_to_index(horizon, index_attendu):
    assert horizon_to_index(horizon) == index_attendu