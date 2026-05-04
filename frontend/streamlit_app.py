"""
streamlit_app.py

Interface complète Vocal Weather.

Fonctionnalités :
- Recherche météo par texte
- Recherche météo via fichier audio
- Recherche météo via micro navigateur
- Affichage des résultats météo
- Carte géographique de la ville détectée
- Graphiques météo sur 7 jours avec Plotly
- Réponse vocale automatique
- Historique des recherches
"""

from datetime import datetime

import folium
import plotly.graph_objects as go
import requests
import streamlit as st
import streamlit.components.v1 as components

from bokeh.models import Button, CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events


# =========================
# CONFIGURATION
# =========================

API_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(
    page_title="Vocal Weather",
    page_icon="🌤️",
    layout="wide",
)


# =========================
# STYLE CSS PERSONNALISÉ
# =========================

st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
}

h1, h2, h3 {
    color: #ffffff;
}

div[data-testid="stBokehChart"] {
    background: transparent !important;
    border: none !important;
}

.weather-box {
    background-color: #111827;
    padding: 1rem;
    border-radius: 14px;
    border: 1px solid #374151;
    margin-top: 1rem;
    margin-bottom: 1rem;
}

.weather-box h3 {
    margin-bottom: 0.4rem;
}

.weather-box p {
    color: #d1d5db;
    margin-bottom: 0;
}

.small-muted {
    color: #9ca3af;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


# =========================
# TEXT TO SPEECH
# =========================

def lire_reponse_orale(texte: str) -> None:
    """
    Lit une réponse à voix haute dans le navigateur.

    Utilise SpeechSynthesis :
    - gratuit
    - intégré à Chrome / Edge
    - aucune clé API nécessaire
    """

    components.html(
        f"""
        <script>
            window.speechSynthesis.cancel();

            const message = new SpeechSynthesisUtterance({texte!r});
            message.lang = "fr-FR";
            message.rate = 1;
            message.pitch = 1;

            window.speechSynthesis.speak(message);
        </script>
        """,
        height=0,
    )


# =========================
# CARTE GÉOGRAPHIQUE
# =========================

def afficher_carte(latitude: float, longitude: float, lieu: str) -> None:
    """
    Affiche une carte Folium centrée sur la ville détectée.

    On utilise components.html() au lieu de st_folium()
    pour éviter les erreurs de sérialisation JSON.
    """

    carte = folium.Map(
        location=[latitude, longitude],
        zoom_start=10,
        tiles="OpenStreetMap",
    )

    folium.Marker(
        location=[latitude, longitude],
        tooltip=lieu,
        popup=f"📍 {lieu}",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(carte)

    st.subheader("🗺️ Localisation")
    components.html(carte._repr_html_(), height=400)


# =========================
# GRAPHIQUES 7 JOURS
# =========================

def afficher_graphiques_7_jours(previsions: list[dict]) -> None:
    """
    Affiche les prévisions météo sur 7 jours avec Plotly.

    Améliorations :
    - tooltips enrichis
    - grille douce
    - ligne moyenne température max
    - barres de pluie lisibles
    """

    if not previsions:
        st.warning("Prévisions 7 jours indisponibles.")
        return

    dates = [
        datetime.strptime(jour["date"], "%Y-%m-%d").strftime("%d/%m")
        for jour in previsions
    ]

    temp_max = [jour["temp_max"] for jour in previsions]
    temp_min = [jour["temp_min"] for jour in previsions]
    precipitations = [jour["precipitation"] for jour in previsions]

    moyenne_temp_max = sum(temp_max) / len(temp_max)

    st.subheader("📊 Prévisions sur 7 jours")

    # -------------------------
    # Graphique températures
    # -------------------------

    fig_temp = go.Figure()

    fig_temp.add_trace(go.Scatter(
        x=dates,
        y=temp_max,
        mode="lines+markers",
        name="Température max",
        line=dict(color="#3b82f6", width=3),
        marker=dict(size=8),
        hovertemplate="Date : %{x}<br>Température max : %{y} °C<extra></extra>",
    ))

    fig_temp.add_trace(go.Scatter(
        x=dates,
        y=temp_min,
        mode="lines+markers",
        name="Température min",
        line=dict(color="#ef4444", width=3),
        marker=dict(size=8),
        hovertemplate="Date : %{x}<br>Température min : %{y} °C<extra></extra>",
    ))

    fig_temp.add_hline(
        y=moyenne_temp_max,
        line_dash="dot",
        line_color="#9ca3af",
        annotation_text=f"Moyenne max : {moyenne_temp_max:.1f} °C",
        annotation_position="top right",
    )

    fig_temp.update_layout(
        title="Températures sur 7 jours",
        xaxis_title="Date",
        yaxis_title="Température (°C)",
        template="plotly_dark",
        height=380,
        margin=dict(l=20, r=20, t=60, b=30),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(
            showgrid=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.12)",
        ),
    )

    st.plotly_chart(fig_temp, use_container_width=True)

    # -------------------------
    # Graphique précipitations
    # -------------------------

    fig_rain = go.Figure()

    fig_rain.add_trace(go.Bar(
        x=dates,
        y=precipitations,
        name="Précipitations",
        marker=dict(color="#6366f1"),
        text=[f"{p} mm" for p in precipitations],
        textposition="outside",
        hovertemplate="Date : %{x}<br>Précipitations : %{y} mm<extra></extra>",
    ))

    fig_rain.update_layout(
        title="Précipitations sur 7 jours",
        xaxis_title="Date",
        yaxis_title="Précipitations (mm)",
        template="plotly_dark",
        height=380,
        margin=dict(l=20, r=20, t=60, b=30),
        xaxis=dict(
            showgrid=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.12)",
        ),
    )

    st.plotly_chart(fig_rain, use_container_width=True)


# =========================
# AFFICHAGE MÉTÉO
# =========================

def badge_meteo(description: str | None) -> str:
    """
    Retourne un badge visuel selon la description météo.
    """

    description_lower = (description or "").lower()

    if "orage" in description_lower:
        return "⛈️ Orage"
    if "pluie" in description_lower or "averse" in description_lower:
        return "🌧️ Pluie"
    if "nuage" in description_lower or "couvert" in description_lower:
        return "☁️ Nuageux"
    if "soleil" in description_lower or "dégagé" in description_lower:
        return "☀️ Ensoleillé"

    return "🌤️ Variable"


def afficher_resultat(data: dict) -> None:
    """
    Affiche les données météo retournées par l'API :
    - résumé météo
    - badge météo
    - carte
    - graphiques 7 jours
    - réponse orale
    """

    meteo = data["meteo"]
    description = meteo.get("description", "")

    st.success(f"📍 {data['lieu']} — horizon : {data['horizon']}")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🌡️ Temp. max", f"{meteo.get('temp_max')} °C")
    col2.metric("❄️ Temp. min", f"{meteo.get('temp_min')} °C")
    col3.metric("🌧️ Pluie", f"{meteo.get('precipitation')} mm")
    col4.metric("💨 Vent", f"{meteo.get('vent_max')} km/h")

    badge = badge_meteo(description)

    st.markdown(f"""
    <div class="weather-box">
        <h3>{badge}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)

    if data.get("texte"):
        st.caption(f"Texte analysé : « {data['texte']} »")

    if data.get("latitude") is not None and data.get("longitude") is not None:
        afficher_carte(
            latitude=data["latitude"],
            longitude=data["longitude"],
            lieu=data["lieu"],
        )

    afficher_graphiques_7_jours(
        data.get("previsions_7_jours", [])
    )

    phrase_orale = (
        f"La météo pour {data['lieu']} {data['horizon']} est : "
        f"{description}. "
        f"La température maximale est de {meteo.get('temp_max')} degrés, "
        f"et la température minimale est de {meteo.get('temp_min')} degrés."
    )

    lire_reponse_orale(phrase_orale)


# =========================
# APPELS API
# =========================

def afficher_erreur_api(response: requests.Response) -> None:
    """
    Affiche une erreur lisible venant de FastAPI.
    """

    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text

    st.error(detail)


def appeler_api_meteo(texte: str) -> None:
    """
    Envoie une phrase météo à l'endpoint /meteo.
    Affiche une progression pour améliorer l'expérience utilisateur.
    """

    if not texte.strip():
        st.warning("Veuillez entrer une question météo.")
        return

    progress = st.progress(0, text="Analyse en cours...")

    try:
        progress.progress(20, text="Extraction de la demande...")

        response = requests.post(
            f"{API_URL}/meteo",
            json={"texte": texte},
            timeout=20,
        )

        progress.progress(60, text="Récupération météo...")

        if response.status_code == 200:
            progress.progress(100, text="Affichage des résultats...")
            progress.empty()
            afficher_resultat(response.json())
        else:
            progress.empty()
            afficher_erreur_api(response)

    except requests.RequestException as e:
        progress.empty()
        st.error(f"Impossible de contacter l'API : {e}")


def appeler_api_audio(fichier_audio) -> None:
    """
    Envoie un fichier audio à l'endpoint /meteo-vocale.
    """

    with st.spinner("Transcription et analyse météo..."):
        try:
            response = requests.post(
                f"{API_URL}/meteo-vocale",
                files={
                    "fichier": (
                        fichier_audio.name,
                        fichier_audio,
                        fichier_audio.type,
                    )
                },
                timeout=30,
            )

            if response.status_code == 200:
                afficher_resultat(response.json())
            else:
                afficher_erreur_api(response)

        except requests.RequestException as e:
            st.error(f"Impossible de contacter l'API : {e}")


# =========================
# INTERFACE PRINCIPALE
# =========================

st.title("🌤️ Vocal Weather")
st.caption("Demandez la météo par texte, fichier audio ou micro 🎤")

col_main, col_history = st.columns([2, 1])


# =========================
# COLONNE PRINCIPALE
# =========================

with col_main:
    st.subheader("🔎 Recherche météo")

    tab_texte, tab_audio, tab_micro = st.tabs(
        ["📝 Texte", "🎧 Fichier audio", "🎤 Micro"]
    )

    # -------------------------
    # TEXTE
    # -------------------------

    with tab_texte:
        texte = st.text_input(
            "Votre question météo",
            placeholder="Ex : Quel temps fera-t-il à Paris demain ?",
            key="texte_input",
        )

        if st.button("Obtenir la météo", type="primary", key="btn_texte"):
            appeler_api_meteo(texte)

    # -------------------------
    # FICHIER AUDIO
    # -------------------------

    with tab_audio:
        st.info(
            "Si STT_PROVIDER=mock dans .env, le contenu réel du fichier audio "
            "est ignoré et une phrase de test est utilisée."
        )

        fichier_audio = st.file_uploader(
            "Fichier audio",
            type=["wav", "mp3", "m4a"],
            help="Formats acceptés : wav, mp3, m4a",
        )

        if fichier_audio is not None:
            st.audio(fichier_audio)

            if st.button("Analyser l'audio", type="primary", key="btn_audio"):
                appeler_api_audio(fichier_audio)

    # -------------------------
    # MICRO
    # -------------------------

    with tab_micro:
        st.info("Fonctionne principalement avec Chrome / Edge.")
        st.write("Cliquez sur le bouton puis dictez votre question météo.")

        bouton_micro = Button(
            label="🎤 Parler",
            button_type="success",
            width=220,
        )

        bouton_micro.js_on_event(
            "button_click",
            CustomJS(
                code="""
                const SpeechRecognition =
                    window.SpeechRecognition || window.webkitSpeechRecognition;

                if (!SpeechRecognition) {
                    document.dispatchEvent(
                        new CustomEvent("GET_TEXT", {
                            detail: "ERREUR: navigateur non compatible"
                        })
                    );
                    return;
                }

                const recognition = new SpeechRecognition();

                recognition.lang = "fr-FR";
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.maxAlternatives = 1;

                recognition.start();

                recognition.onresult = function(event) {
                    const texte = event.results[0][0].transcript;

                    document.dispatchEvent(
                        new CustomEvent("GET_TEXT", { detail: texte })
                    );
                };

                recognition.onerror = function(event) {
                    document.dispatchEvent(
                        new CustomEvent("GET_TEXT", {
                            detail: "ERREUR MICRO: " + event.error
                        })
                    );
                };
                """
            ),
        )

        result = streamlit_bokeh_events(
            bouton_micro,
            events="GET_TEXT",
            key="micro_event",
            refresh_on_update=False,
            override_height=80,
            debounce_time=0,
        )

        if result and "GET_TEXT" in result:
            texte_micro = result["GET_TEXT"]

            if texte_micro.startswith("ERREUR"):
                st.error(texte_micro)
            else:
                st.success(f"🎤 Texte reconnu : {texte_micro}")
                appeler_api_meteo(texte_micro)


# =========================
# COLONNE HISTORIQUE
# =========================

with col_history:
    st.subheader("📜 Historique")

    if st.button("Actualiser", key="btn_historique"):
        st.rerun()

    try:
        response = requests.get(
            f"{API_URL}/historique",
            timeout=10,
        )

        if response.status_code == 200:
            historique = response.json().get("historique", [])

            if not historique:
                st.info("Aucune recherche pour le moment.")
            else:
                historique_trie = sorted(
                    historique,
                    key=lambda x: x.get("timestamp", ""),
                    reverse=True,
                )

                for item in historique_trie[:10]:
                    titre = (
                        f"{item.get('lieu_detecte') or '?'} "
                        f"— {item.get('horizon')}"
                    )

                    with st.expander(titre):
                        st.write(f"**Texte :** {item.get('texte_brut')}")
                        st.write(f"**Date :** {item.get('timestamp')}")
                        st.write(f"**Statut :** {item.get('statut')}")

                        if item.get("description"):
                            st.write(f"**Météo :** {item.get('description')}")
                            st.write(f"**Temp. max :** {item.get('temp_max')} °C")
                            st.write(f"**Temp. min :** {item.get('temp_min')} °C")

        else:
            st.warning("Impossible de charger l'historique.")

    except requests.RequestException:
        st.warning("API non disponible. Lance d'abord FastAPI.")