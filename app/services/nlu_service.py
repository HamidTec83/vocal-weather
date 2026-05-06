"""
nlu_service.py

Contient la logique NLU simple du projet.

NLU = Natural Language Understanding

Objectif :
- Comprendre une phrase utilisateur
- Extraire le lieu demandé
- Extraire l'horizon temporel
- Détecter aussi un code postal français

Exemples :
"Quel temps fera-t-il à Paris demain ?"

Devient :
{
    "lieu": "Paris",
    "horizon": "demain"
}

"Météo à 75018 demain"

Devient :
{
    "lieu": "75018",
    "horizon": "demain"
}
"""

import re


def extraire_intention(texte: str) -> dict:
    """
    Extrait le lieu et l'horizon temporel depuis un texte.

    Paramètre :
    - texte : phrase utilisateur ou phrase transcrite depuis la voix

    Retour :
    {
        "lieu": str | None,
        "horizon": str
    }
    """

    texte_lower = texte.lower().strip()

    # =========================
    # Extraction de l'horizon
    # =========================

    horizon = "aujourd'hui"

    if "après-demain" in texte_lower or "apres-demain" in texte_lower:
        horizon = "j+2"

    elif "demain" in texte_lower:
        horizon = "demain"

    elif "semaine" in texte_lower or "7 jours" in texte_lower:
        horizon = "semaine"

    elif match := re.search(r"dans (\d+) jours?", texte_lower):
        horizon = f"j+{match.group(1)}"

    # =========================
    # Extraction du lieu
    # =========================

    lieu = None

    # 1. Priorité au code postal français : 5 chiffres
    # Exemples : 75018, 69003, 13001, 37000
    match_code_postal = re.search(r"\b\d{5}\b", texte_lower)

    if match_code_postal:
        lieu = match_code_postal.group(0)

    else:
        # 2. Sinon, extraction classique d'un nom de ville
        match_lieu = re.search(
            r"(?:à|a|sur|pour|en|de|près de|pres de)\s+([a-zà-öø-ÿ\- ]+)",
            texte_lower
        )

        if match_lieu:
            brut = match_lieu.group(1).strip()

            stop_words = [
                "demain",
                "après-demain",
                "apres-demain",
                "dans",
                "jour",
                "jours",
                "semaine",
                "aujourd'hui",
                "cette",
            ]

            mots = brut.split()
            lieu_mots = []

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
            return min(index, 6)

        except ValueError:
            return 0

    return 0