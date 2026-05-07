"""
nlu_service.py

Contient la logique NLU (Natural Language Understanding) du projet.
NLU = Compréhension du langage naturel.

Objectif :
- Analyser la phrase utilisateur pour extraire :
  1. le lieu (ville ou code postal)
  2. l'horizon temporel (aujourd'hui, demain, j+2...)
  3. l'heure précise si elle est demandée (ex: 20h)
"""

import re


def extraire_heure(texte_lower: str) -> int | None:
    """
    Détecte une heure dans la phrase utilisateur.

    Exemples reconnus :
    - 20h
    - 20 h
    - 20heure
    - 20 heures
    - à 20h
    - vers 18h
    """

    # On accepte aussi le format compact "20h"
    match = re.search(r"\b([01]?\d|2[0-3])\s*(?:h|heure|heures)?\b", texte_lower)
    if not match:
        return None

    try:
        heure = int(match.group(1))
        if 0 <= heure <= 23:
            return heure
    except ValueError:
        return None

    return None


def extraire_intention(texte: str) -> dict:
    """
    Extrait le lieu, l'horizon temporel et l'heure éventuelle.
    Retour :
    {
        "lieu": str | None,
        "horizon": str,
        "heure": int | None
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
    # Extraction de l'heure
    # =========================

    heure = extraire_heure(texte_lower)

    # =========================
    # Extraction du lieu
    # =========================

    lieu = None

    # 1) Priorité au code postal français
    match_code_postal = re.search(r"\b\d{5}\b", texte_lower)
    if match_code_postal:
        lieu = match_code_postal.group(0)

    else:
        # 2) Sinon, on cherche le lieu après une préposition
        # On capture jusqu'à un mot temporel ou une heure
        match_lieu = re.search(
            r"(?:à|a|sur|pour|en|de|près de|pres de)\s+([a-zà-öø-ÿ\- ]+)",
            texte_lower
        )

        if match_lieu:
            brut = match_lieu.group(1).strip()

            # Mots qui indiquent qu'on a dépassé le nom du lieu
            stop_words = {
                "demain",
                "après-demain",
                "apres-demain",
                "dans",
                "jour",
                "jours",
                "semaine",
                "aujourd'hui",
                "aujourdhui",
                "aujourd",
                "cette",
                "vers",
                "à",
                "a",
                "h",
                "heure",
                "heures",
                "matin",
                "midi",
                "soir",
                "nuit",
            }

            mots = brut.split()
            lieu_mots = []

            for mot in mots:
                mot_nettoye = mot.strip(" ?!,.;:'\"")

                # On stoppe si on tombe sur un mot temporel
                if mot_nettoye in stop_words:
                    break

                # On stoppe aussi si on voit une heure du type 20h
                if re.fullmatch(r"([01]?\d|2[0-3])h?", mot_nettoye):
                    break

                lieu_mots.append(mot_nettoye)

            if lieu_mots:
                lieu = " ".join(lieu_mots).title()

    return {
        "lieu": lieu,
        "horizon": horizon,
        "heure": heure,
    }


def horizon_to_index(horizon: str) -> int:
    """
    Convertit un horizon temporel en index de jour.

    Correspondance :
    - "aujourd'hui" -> 0
    - "demain" -> 1
    - "j+2" -> 2
    - ...
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