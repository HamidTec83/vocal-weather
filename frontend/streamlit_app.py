"""
streamlit_app.py

Interface complète Vocal Weather :

Fonctionnalités :
- Recherche météo par texte
- Recherche via micro navigateur
- Affichage des résultats
- Historique
- 🔊 Réponse orale automatique (Text-to-Speech)

Technos :
- Streamlit
- FastAPI (backend)
- Web Speech API (micro + voix)
"""

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

# Supprime le fond gris du bouton micro (Bokeh)
st.markdown("""
<style>
div[data-testid="stBokehChart"] {
    background: transparent !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)


# =========================
# TEXT TO SPEECH 🔊
# =========================

def lire_reponse_orale(texte: str) -> None:
    """
    Lit une phrase à voix haute dans le navigateur.

    Utilise SpeechSynthesis :
    - gratuit
    - intégré à Chrome / Edge
    """

    components.html(
        f"""
        <script>
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
# AFFICHAGE RESULTAT
# =========================

def afficher_resultat(data: dict) -> None:
    """
    Affiche la météo + déclenche la réponse orale.
    """

    meteo = data["meteo"]

    st.success(f"📍 {data['lieu']} — horizon : {data['horizon']}")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🌡️ Temp. max", f"{meteo.get('temp_max')} °C")
    col2.metric("❄️ Temp. min", f"{meteo.get('temp_min')} °C")
    col3.metric("🌧️ Pluie", f"{meteo.get('precipitation')} mm")
    col4.metric("💨 Vent", f"{meteo.get('vent_max')} km/h")

    st.info(f"Conditions : {meteo.get('description')}")

    # -------------------------
    # 🔊 PHRASE ORALE
    # -------------------------
    phrase = (
        f"La météo pour {data['lieu']} {data['horizon']} est {meteo.get('description')}. "
        f"La température maximale est de {meteo.get('temp_max')} degrés, "
        f"et la minimale est de {meteo.get('temp_min')} degrés."
    )

    lire_reponse_orale(phrase)


# =========================
# APPEL API
# =========================

def appeler_api_meteo(texte: str) -> None:
    """
    Envoie la requête texte au backend FastAPI.
    """

    if not texte.strip():
        st.warning("Veuillez entrer une question.")
        return

    with st.spinner("Analyse en cours..."):
        try:
            response = requests.post(
                f"{API_URL}/meteo",
                json={"texte": texte},
                timeout=20,
            )

            if response.status_code == 200:
                afficher_resultat(response.json())
            else:
                st.error(response.text)

        except Exception as e:
            st.error(f"Erreur API : {e}")


# =========================
# INTERFACE
# =========================

st.title("🌤️ Vocal Weather")
st.caption("Demandez la météo par texte ou micro 🎤")

col_main, col_history = st.columns([2, 1])


# =========================
# PARTIE PRINCIPALE
# =========================

with col_main:

    st.subheader("🔎 Recherche météo")

    tab1, tab2 = st.tabs(["📝 Texte", "🎤 Micro"])

    # -------------------------
    # TEXTE
    # -------------------------
    with tab1:
        texte = st.text_input(
            "Votre question météo",
            placeholder="Ex: Quel temps fera-t-il à Paris demain ?"
        )

        if st.button("Obtenir la météo"):
            appeler_api_meteo(texte)

    # -------------------------
    # MICRO 🎤
    # -------------------------
    with tab2:

        st.info("Fonctionne avec Chrome / Edge.")

        st.write("Cliquez puis parlez.")

        # Bouton JS
        bouton = Button(label="🎤 Parler", button_type="success")

        bouton.js_on_event(
            "button_click",
            CustomJS(code="""
                const SpeechRecognition =
                    window.SpeechRecognition || window.webkitSpeechRecognition;

                if (!SpeechRecognition) {
                    document.dispatchEvent(
                        new CustomEvent("GET_TEXT", {
                            detail: "ERREUR navigateur"
                        })
                    );
                    return;
                }

                const recognition = new SpeechRecognition();
                recognition.lang = "fr-FR";

                recognition.start();

                recognition.onresult = function(event) {
                    const texte = event.results[0][0].transcript;

                    document.dispatchEvent(
                        new CustomEvent("GET_TEXT", { detail: texte })
                    );
                };
            """)
        )

        # Capture événement JS
        result = streamlit_bokeh_events(
            bouton,
            events="GET_TEXT",
            key="mic",
            refresh_on_update=False,
            override_height=80,
        )

        if result and "GET_TEXT" in result:
            texte_micro = result["GET_TEXT"]

            st.success(f"🎤 Texte reconnu : {texte_micro}")

            appeler_api_meteo(texte_micro)


# =========================
# HISTORIQUE
# =========================

with col_history:

    st.subheader("📜 Historique")

    if st.button("Actualiser"):
        st.rerun()

    try:
        response = requests.get(f"{API_URL}/historique")

        if response.status_code == 200:
            historique = response.json()["historique"]

            for item in historique[:10]:
                with st.expander(f"{item['lieu_detecte']} — {item['horizon']}"):
                    st.write(item["texte_brut"])
                    st.write(item["description"])

    except:
        st.warning("API non disponible")