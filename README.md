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
- ⏰ Extraction de l'heure précise (ex : à 20h)
- 🌦️ Appel à l'API Open-Meteo (gratuit, sans clé)
- 🔊 Réponse vocale automatique (Text-to-Speech)
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
Lieu + horizon temporel + heure
   ↓
Open-Meteo API
   ↓
Prévisions météo (journalière ou horaire)
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
| Géocodage CP    | geo.api.gouv.fr               |
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
- Support des codes postaux français (ex : 75018)
- Météo à l'heure précise (ex : "à Paris à 20h")
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
- comprend la demande (lieu + horizon + heure éventuelle)
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
# Windows
.\venv\Scripts\Activate.ps1

# Linux / Mac
source venv/bin/activate
```

**4. Installer les dépendances**
```bash
pip install -r requirements.txt
```

**5. Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env si nécessaire (clé OpenAI optionnelle)
```

---

## ▶️ Lancement du projet

**Backend FastAPI** (terminal 1)
```bash
uvicorn app.main:app --reload
```
Swagger : http://127.0.0.1:8000/docs

**Frontend Streamlit** (terminal 2)
```bash
streamlit run frontend/streamlit_app.py
```
Interface : http://localhost:8501

---

## 🔗 Endpoints API

| Méthode | Endpoint                 | Description                    |
| ------- | ------------------------ | ------------------------------ |
| POST    | `/api/v1/meteo`          | Obtenir la météo depuis texte  |
| POST    | `/api/v1/transcrire`     | Transcrire un fichier audio    |
| POST    | `/api/v1/meteo-vocale`   | Pipeline complet audio → météo |
| POST    | `/api/v1/feedback`       | Envoyer un feedback            |
| GET     | `/api/v1/feedback/stats` | Statistiques feedback          |
| GET     | `/api/v1/historique`     | Historique des recherches      |
| GET     | `/api/v1/health`         | Vérifier l'état de l'API       |

---

## 🔐 Sécurité (OWASP)

- ✅ Validation des entrées avec Pydantic
- ✅ Rate limiting via SlowAPI
- ✅ Variables sensibles dans `.env`
- ✅ Requêtes SQLite préparées (anti-injection)
- ✅ Headers de sécurité HTTP personnalisés
- ✅ Validation des fichiers audio uploadés

---

## 🧪 Tests

Le projet dispose d'une suite de tests unitaires et d'intégration.

```bash
# Lancer tous les tests
pytest tests/ -v

# Avec couverture de code
pytest --cov=app --cov-report=term-missing
```

### Résultat actuel

```
✅ 68 passed
Coverage total : 98%
```

### Types de tests

- **Tests unitaires NLU** — extraction lieu, horizon, heure (regex)
- **Tests unitaires Weather service** — API Open-Meteo mockée
- **Tests unitaires STT** — mode mock et OpenAI simulé
- **Tests d'intégration API** — `/meteo`, `/feedback`, `/health`
- **Tests pipeline complet** — texte et audio
- **Tests base de données** — SQLite avec base temporaire isolée

### Bonnes pratiques appliquées

- Aucun appel réseau réel pendant les tests
- Utilisation de `monkeypatch` pour mocker Open-Meteo, OpenAI et SQLite

---

## ⚠️ Limitations

- Le micro fonctionne principalement avec Chrome / Edge
- L'extraction NLU est basée sur des regex (limites sur phrases complexes)
- Le STT backend est en mode mock par défaut (Whisper optionnel)

---

## ✅ État du projet

Projet fonctionnel en local avec :

- Interface Streamlit complète
- API FastAPI sécurisée
- Pipeline vocal opérationnel
- Météo journalière et horaire
- Visualisations et feedback utilisateur

Prêt pour amélioration ou déploiement.

---

## 🚀 Améliorations futures

- Intégration de Whisper (STT avancé)
- Utilisation d'un LLM pour le NLU
- Dockerisation de l'application
- Déploiement en ligne (Render / Railway)
- Authentification utilisateur

---

## 🔑 Variables d'environnement

| Variable         | Description                          | Obligatoire |
| ---------------- | ------------------------------------ | ----------- |
| `OPENAI_API_KEY` | Clé API OpenAI (pour Whisper)        | Non         |
| `DB_PATH`        | Chemin vers la base SQLite           | Non (défaut : `data/vocal_weather.db`) |
| `STT_PROVIDER`   | Fournisseur STT (`mock` ou `whisper`) | Non (défaut : `mock`) |
| `APP_HOST`       | Hôte du serveur FastAPI              | Non (défaut : `127.0.0.1`) |
| `APP_PORT`       | Port du serveur FastAPI              | Non (défaut : `8000`) |

---

## 👨‍💻 Auteur

Projet réalisé par **Hamid** — [GitHub](https://github.com/HamidTec83)
