import streamlit as st
import pandas as pd
import os

from script1 import clean_database_with_output
from script2 import classify_flows
from script3 import run_script3
from script4 import run_script4
from script5 import process_geography
from script6 import main as run_script6

st.set_page_config(page_title="Workflow Analisi Dati", layout="wide")

# === Sidebar Navigation ===
menu = st.sidebar.selectbox(
    "📁 Seleziona un flusso:",
    [
        "🏠 Home",
        "1. Flusso principale (script 1–6)",
        "2. Analisi supplementare",
        "3. Reportistica",
        "4. Validazione finale",
        "5. Esportazione & salvataggio"
    ]
)

# === Home Page ===
if menu == "🏠 Home":
    st.title("📦 Tool di Elaborazione Dati Makeitalia")
    st.markdown("""
    Benvenuto nel tool automatizzato per l’elaborazione dei dati logistici.

    ### 📋 Istruzioni:
    1. Vai alla sezione **"1. Flusso principale"**
    2. Carica il file Excel da pulire
    3. Scarica il risultato e le righe eliminate
    4. (Opzionale) Carica una versione modificata del file pulito
    5. Inserisci le ragioni sociali richieste
    6. Avvia la sequenza degli script
    """)

# === Flusso 1: Script 1 → 6 ===
elif menu == "1. Flusso principale (script 1–6)":
    st.title("🧩 Flusso Principale - Script 1 → 6")

    uploaded_file = st.file_uploader("📤 Carica il file Excel da elaborare", type=["xlsx"])

    if uploaded_file:
        with open("input_file.xlsx", "wb") as f:
            f.write(uploaded_file.read())

        st.success("✅ File caricato correttamente")

        if st.button("▶️ Avvia Script 1 (pulizia)"):
            clean_database_with_output("input_file.xlsx", "database_pulito.xlsx", "righe_eliminate.xlsx")
            st.success("✅ Script 1 completato!")
            with open("database_pulito.xlsx", "rb") as f1:
                st.download_button("⬇️ Scarica file pulito", f1, "database_pulito.xlsx")
            with open("righe_eliminate.xlsx", "rb") as f2:
                st.download_button("⬇️ Scarica righe eliminate", f2, "righe_eliminate.xlsx")

    st.divider()
    uploaded_modified = st.file_uploader("📤 Carica versione modificata (opzionale)", type=["xlsx"], key="modificato")
    file_to_use = None

    if uploaded_modified:
        with open("database_modificato.xlsx", "wb") as f:
            f.write(uploaded_modified.read())
        file_to_use = "database_modificato.xlsx"
        st.success("✅ File modificato caricato")
    elif os.path.exists("database_pulito.xlsx"):
        file_to_use = "database_pulito.xlsx"

    if file_to_use:
        st.markdown("### ✏️ Inserisci le ragioni sociali")
        inbound_input = st.text_input("INBOUND – scrivi nomi separati da virgola", "")
        outbound_input = st.text_input("OUTBOUND – scrivi nomi separati da virgola", "")
        nav_input = st.text_input("NAVETTAGGIO – scrivi nomi separati da virgola", "")

        if st.button("🚀 Esegui Script 2 → 6"):
            inbound = [r.strip() for r in inbound_input.split(",") if r.strip()]
            outbound = [r.strip() for r in outbound_input.split(",") if r.strip()]
            nav = [r.strip() for r in nav_input.split(",") if r.strip()]

            if not (inbound or outbound or nav):
                st.error("⚠️ Inserisci almeno una ragione sociale per continuare.")
                st.stop()

            classify_flows(file_to_use, "database_classificato.xlsx", inbound, outbound, nav)
            run_script3("database_classificato.xlsx", "database_dimensioni.xlsx")

            if not os.path.exists("fasce di peso.xlsx"):
                st.error("❌ Manca il file 'fasce di peso.xlsx'. Aggiungilo nella directory.")
                st.stop()

            run_script4("database_dimensioni.xlsx", "fasce di peso.xlsx", "database_fascia di peso.xlsx")

            if not os.path.exists("geografia.xlsx"):
                st.error("❌ Manca il file 'geografia.xlsx'. Aggiungilo nella directory.")
                st.stop()

            process_geography("database_fascia di peso.xlsx", "geografia.xlsx", "database arricchito con geografia.xlsx")
            run_script6()

            st.success("✅ Tutti gli script sono stati eseguiti correttamente!")

            with open("output_tratte_completo.xlsx", "rb") as f:
                st.download_button("⬇️ Scarica file finale", f, "output_tratte_completo.xlsx")

# === Sezioni non ancora attive ===
else:
    st.warning("🚧 Sezione in sviluppo. Torna presto.")