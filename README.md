# 🌤️ Vocal Weather

> Application météo vocale intelligente — Speech-to-Text, NLU, API météo, Text-to-Speech, visualisations et feedback utilisateur.

Vocal Weather est une application web permettant d'obtenir la météo  
à partir d'une commande vocale, d'un texte ou d'un fichier audio.

L'utilisateur peut demander :

> Quel temps fera-t-il à Lyon demain ?

L'application transcrit la voix, extrait l'intention météo, interroge  
une API météo, affiche les prévisions, répond à l'oral et sauvegarde  
l'historique des recherches.

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
- 🗺️ Carte géographique de la ville détectée (Folium)
- 📊 Graphiques météo sur 7 jours (Plotly)
- 👍👎 Feedback utilisateur
- 📈 Dashboard feedback
- 🔐 Validation des entrées (Pydantic)
- 🚦 Rate limiting (SlowAPI)
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
Affichage + réponse vocale + feedback
```

---

## 🛠️ Stack technique

| Composant       | Technologie                   |
| --------------- | ----------------------------- |
| Frontend        | Streamlit                     |
| Backend         | FastAPI                       |
| STT             | Web Speech API                |
| TTS             | SpeechSynthesis API           |
| NLU             | Regex Python                  |
| API météo       | Open-Meteo                    |
| Base de données | SQLite                        |
| Carte           | Folium                        |
| Graphiques      | Plotly                        |
| Sécurité        | SlowAPI + validation Pydantic |
| Tests           | pytest                        |
| Versioning      | Git / GitHub                  |

---

## ⭐ Points forts

- Pipeline IA complet (STT → NLU → API → TTS)
- Interface utilisateur simple et intuitive
- Expérience vocale bidirectionnelle
- Visualisations interactives (carte + graphiques)
- Système de feedback utilisateur intégré
- Sécurité inspirée des bonnes pratiques OWASP
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
│   ├── security/
│   │   ├── headers.py
│   │   └── rate_limit.py
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
- affiche la météo sur carte et graphiques
- répond à l'oral
- enregistre la recherche et le feedback

---

## 📊 Visualisation des données

L'application propose :

- 🗺️ Carte interactive de la ville détectée (Folium)
- 📈 Graphique des températures sur 7 jours (Plotly)
- 🌧️ Graphique des précipitations sur 7 jours
- 📊 Dashboard de suivi des feedbacks utilisateurs

Ces visualisations permettent une meilleure compréhension des tendances météo.

---

## ⚙️ Installation

**1. Cloner le dépôt**
```bash
git clone https://github.com/HamidTec83/vocal-weather.git
cd vocal-weather
```

**2. Créer un environnement virtuel**
```bash
python -m venv venv
```

**3. Activer l'environnement**
```bash
.\venv\Scripts\Activate.ps1
```

**4. Installer les dépendances**
```bash
pip install -r requirements.txt
```

---

---

## ▶️ Lancement du projet

**Backend FastAPI**
```bash
uvicorn app.main:app --reload
```
Swagger : http://127.0.0.1:8000/docs

**Frontend Streamlit**
```bash
streamlit run frontend/streamlit_app.py
```
Interface : http://localhost:8501

---

## 🔗 Endpoints API

| Méthode | Endpoint                 | Description               |
| ------- | ------------------------ | ------------------------- |
| POST    | `/api/v1/meteo`          | Obtenir la météo          |
| POST    | `/api/v1/feedback`       | Envoyer un feedback       |
| GET     | `/api/v1/feedback/stats` | Statistiques feedback     |
| GET     | `/api/v1/historique`     | Historique des recherches |
| GET     | `/api/v1/health`         | Vérifier l'état de l'API  |

---

## 🔐 Sécurité (OWASP)

- ✅ Validation des entrées avec Pydantic
- ✅ Rate limiting via SlowAPI (3 requêtes/minute)
- ✅ Variables sensibles dans `.env`
- ✅ Requêtes SQLite préparées (anti-injection)
- ✅ CORS restreint au frontend
- ✅ Validation des fichiers audio uploadés

---

## 🧪 Tests

```bash
pytest tests/ -v
```

---

## ⚠️ Limitations

- Le micro fonctionne principalement avec Chrome / Edge
- L'extraction NLU est basée sur des regex (limites sur phrases complexes)
- Le STT backend est en mode mock (pas encore Whisper)

---

## ✅ État du projet

Projet fonctionnel en local avec :

- Interface Streamlit complète
- API FastAPI sécurisée
- Pipeline vocal opérationnel
- Visualisations et feedback utilisateur

Prêt pour amélioration ou déploiement.

---
---

## 🚀 Améliorations futures

- Intégration de Whisper (STT avancé)
- Utilisation d'un LLM pour le NLU
- Dockerisation de l'application
- Déploiement en ligne (Render / Railway)
- Authentification utilisateur

---

## 👨‍💻 Auteur

Projet réalisé par **Hamid** — [GitHub](https://github.com/HamidTec83)