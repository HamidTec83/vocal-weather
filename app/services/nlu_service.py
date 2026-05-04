"""
nlu_service.py

Contient la logique NLU simple du projet.

NLU = Natural Language Understanding

Objectif :
- Comprendre une phrase utilisateur
- Extraire le lieu demandé
- Extraire l'horizon temporel

Exemple :
"Quel temps fera-t-il à Paris demain ?"

Devient :
{
    "lieu": "Paris",
    "horizon": "demain"
}
"""

import re


def extraire_intention(texte: str) -> dict:
    """
    Extrait le lieu et l'horizon temporel depuis un texte.

    Paramètre :
    - texte : phrase transcrite depuis la voix

    Retour :
    {
        "lieu": str | None,
        "horizon": str
    }
    """

    # Normalisation du texte :
    # - minuscules
    # - suppression des espaces au début et à la fin
    texte_lower = texte.lower().strip()

    # =========================
    # Extraction de l'horizon
    # =========================

    # Valeur par défaut si l'utilisateur ne précise rien.
    horizon = "aujourd'hui"

    # Important : tester "après-demain" AVANT "demain"
    # car "après-demain" contient le mot "demain".
    if "après-demain" in texte_lower or "apres-demain" in texte_lower:
        horizon = "j+2"

    elif "demain" in texte_lower:
        horizon = "demain"

    elif "semaine" in texte_lower or "7 jours" in texte_lower:
        horizon = "semaine"

    # Exemple :
    # "dans 3 jours" -> "j+3"
    elif match := re.search(r"dans (\d+) jours?", texte_lower):
        horizon = f"j+{match.group(1)}"

    # =========================
    # Extraction du lieu
    # =========================

    lieu = None

    # Cherche un lieu après des mots fréquents :
    # "à Paris", "a Lyon", "pour Bordeaux", "près de Lille", etc.
    match_lieu = re.search(
        r"(?:à|a|sur|pour|en|de|près de|pres de)\s+([a-zà-öø-ÿ\- ]+)",
        texte_lower
    )

    if match_lieu:
        brut = match_lieu.group(1).strip()

        # Mots qui indiquent que le nom du lieu est terminé.
        stop_words = [
            "demain",
            "après-demain",
            "apres-demain",
            "dans",
            "jour",
            "jours",
            "semaine",
            "aujourd'hui"
        ]

        mots = brut.split()

        lieu_mots = []

        # On ajoute les mots un par un jusqu'à rencontrer un mot temporel.
        for mot in mots:
            if mot in stop_words:
                break

            lieu_mots.append(mot)

        if lieu_mots:
            lieu = " ".join(lieu_mots).title()

    return {
        "lieu": lieu,
        "horizon": horizon
    }


def horizon_to_index(horizon: str) -> int:
    """
    Convertit un horizon temporel en index de jour.

    Correspondance :
    - "aujourd'hui" -> 0
    - "demain"      -> 1
    - "j+2"         -> 2
    - "j+3"         -> 3

    Retourne toujours un index entre 0 et 6,
    car Open-Meteo récupère 7 jours de prévisions.
    """

    if horizon == "aujourd'hui":
        return 0

    if horizon == "demain":
        return 1

    if horizon == "semaine":
        return 0

    if horizon.startswith("j+"):
        try:
            index = int(horizon[2:])

            # Sécurité : forecast_days=7 donne les index 0 à 6.
            return min(index, 6)

        except ValueError:
            return 0

    return 0