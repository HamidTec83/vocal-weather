# 🌤️ Vocal Weather

## > Application météo vocale intelligente — Speech-to-Text + NLP + API météo + Text-to-Speech

Vocal Weather est une application web permettant d'obtenir la météo  
à partir d'une commande vocale ou textuelle.

L'utilisateur peut demander :

> Quel temps fera-t-il à Lyon demain ?

L'application transcrit la voix, extrait l'intention météo, interroge  
une API météo, affiche les prévisions et sauvegarde l'historique des recherches.

---

## 🚀 Fonctionnalités

- 🎤 Reconnaissance vocale via le navigateur
- 📝 Recherche météo par texte
- 🎧 Upload de fichier audio
- 🧠 Extraction du lieu et de l'horizon temporel
- 🌦️ Appel à l'API Open-Meteo
- 🔊 Réponse vocale automatique
- 💾 Sauvegarde des requêtes en SQLite
- 📜 Historique des recherches
- ⚙️ API REST FastAPI documentée avec Swagger

---

## 🧱 Architecture

```text
Utilisateur
   ↓
Interface Streamlit
   ↓
Speech-to-Text / Web Speech API
   ↓
Texte transcrit
   ↓
NLU (Extraction d'intention - Regex)
   ↓
Lieu + horizon temporel
   ↓
Open-Meteo API
   ↓
Prévisions météo
   ↓
SQLite
   ↓
Affichage + réponse vocale
```

---

## 🛠️ Stack technique

| Composant       | Technologie         |
| --------------- | ------------------- |
| Frontend        | Streamlit           |
| Backend         | FastAPI             |
| STT             | Web Speech API      |
| TTS             | SpeechSynthesis API |
| NLU             | Regex Python        |
| API météo       | Open-Meteo          |
| Base de données | SQLite              |
| Tests           | pytest              |
| Versioning      | Git / GitHub        |

---


## ⭐ Points forts

- Pipeline IA complet (STT → NLU → API → TTS)
- Interface utilisateur simple et intuitive
- Expérience vocale bidirectionnelle
- Architecture modulaire (services séparés)
- Projet facilement extensible

---

## 📁 Structure du projet

```text
vocal-weather/
├── app/
│   ├── database/
│   │   ├── db.py
│   │   └── models.py
│   ├── routers/
│   │   ├── voice.py
│   │   └── weather.py
│   ├── services/
│   │   ├── nlu_service.py
│   │   ├── stt_service.py
│   │   └── weather_service.py
│   ├── config.py
│   └── main.py
│
├── data/
│   └── .gitkeep
│
├── docs/
│   └── user_guide.md
│
├── frontend/
│   └── streamlit_app.py
│
├── tests/
│   ├── test_api.py
│   ├── test_nlu_service.py
│   ├── test_stt_service.py
│   └── test_weather_service.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🎬 Démo

Exemple d'utilisation :

> 🎤 "Quel temps fera-t-il à Lyon demain ?"

✔ L'application :
- transcrit la voix
- comprend la demande
- affiche la météo
- répond à l’oral

---

## ⚠️ Limitations

- Le micro fonctionne uniquement avec Chrome / Edge
- L'extraction NLU est basée sur des regex (limites sur phrases complexes)
- Le STT backend est en mode mock (pas encore Whisper)

---

## 🚀 Améliorations futures

- Intégration de Whisper (STT avancé)
- Utilisation d’un LLM pour le NLU
- Ajout de graphiques météo
- Carte géographique
- Déploiement en ligne

---