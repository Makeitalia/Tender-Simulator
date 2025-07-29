import streamlit as st

st.set_page_config(page_title="Workflow Analisi Dati - Makeitalia", layout="wide")

# === Sidebar per la navigazione ===
st.sidebar.title("Workflow Analisi Dati")
sezione = st.sidebar.radio("Seleziona una sezione:", [
    "🏠 Home",
    "🛠 1. Flusso principale",
    "🚧 2. Analisi volumi",
    "🚧 3. KPI principali",
    "🚧 4. Analisi geografica"
])

# === Sezioni dinamiche ===
if sezione == "🏠 Home":
    st.title("📊 Tool Analisi Dati - Makeitalia")
    st.markdown("""
    Benvenuto nel tool interattivo per l'analisi dei dati di tender.

    **Cosa puoi fare:**
    - Eseguire passo dopo passo il processo di pulizia, classificazione e arricchimento del database
    - Scaricare i file intermedi per eventuali verifiche o modifiche
    - Eseguire script in modo guidato, anche senza conoscenze tecniche

    Usa il menu a sinistra per iniziare 👈
    """)

elif sezione == "🛠 1. Flusso principale":
    from pages.sezione_flusso_principale import run as run_flusso
    run_flusso()

elif sezione.startswith("🚧"):
    st.title(sezione)
    st.warning("🧱 Questa sezione è ancora in fase di sviluppo. Torna presto!")