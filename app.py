import streamlit as st
import os
import pandas as pd
from script1 import clean_database_with_output
from script2 import classify_flows
from script3 import run_script3
from script4 import run_script4
from script5 import process_geography
from script6 import main as run_script6

# === Configurazione pagina ===
st.set_page_config(page_title="Workflow Analisi Dati", layout="wide")
st.title("📊 Workflow Analisi Dati - Tool Makeitalia")

upload_dir = "uploaded_files"
os.makedirs(upload_dir, exist_ok=True)

# === Menu laterale ===
menu = st.sidebar.selectbox("📁 Seleziona sezione", [
    "Home",
    "Step 1 - Pulizia iniziale",
    "Step 2 - Classificazione Flussi",
    "Step 3 - Dimensioni / Fasce",
    "Step 4 - Geografia",
    "Step 5 - Finalizzazione"
])

# === HOME ===
if menu == "Home":
    st.header("ℹ️ Benvenuto nel Tool per Analisi Dati")
    st.markdown("""
    Questo strumento guida l'utente nell'esecuzione step-by-step di una serie di script per la pulizia e l'arricchimento dei dati logistici.

    ### ✅ Flusso supportato:
    1. Caricamento e pulizia del file iniziale
    2. Classificazione dei flussi (inbound, outbound, navettaggio)
    3. Aggiunta dimensioni e fasce di peso
    4. Arricchimento geografico
    5. Output finale con ID, frequenze e pesi

    Tutti i file intermedi possono essere scaricati. Buon lavoro!
    """)

# === STEP 1 - PULIZIA ===
elif menu == "Step 1 - Pulizia iniziale":
    st.header("🧹 Step 1 - Pulizia iniziale")
    file1 = st.file_uploader("📂 Carica il file Excel da analizzare", type=["xlsx"], key="upload1")

    if file1:
        path_input = os.path.join(upload_dir, "input_file.xlsx")
        with open(path_input, "wb") as f:
            f.write(file1.read())

        output_clean = "database_pulito.xlsx"
        output_removed = "righe_eliminate.xlsx"

        clean_database_with_output(path_input, output_clean, output_removed)
        st.success("✅ File pulito con successo.")
        st.download_button("⬇️ Scarica database pulito", open(output_clean, "rb"), file_name=output_clean)
        st.download_button("⬇️ Scarica righe eliminate", open(output_removed, "rb"), file_name=output_removed)

# === STEP 2 - CLASSIFICAZIONE ===
elif menu == "Step 2 - Classificazione Flussi":
    st.header("🧭 Step 2 - Classificazione flussi")
    file2 = st.file_uploader("📂 Carica il file pulito", type="xlsx", key="upload2")

    inbound = st.text_input("✏️ Ragioni sociali INBOUND (separate da virgola)")
    outbound = st.text_input("✏️ Ragioni sociali OUTBOUND (separate da virgola)")
    navettaggio = st.text_input("✏️ Ragioni sociali NAVETTAGGIO (separate da virgola)")

    if file2 and st.button("▶️ Esegui Script 2"):
        path = "database_pulito_step2.xlsx"
        with open(path, "wb") as f:
            f.write(file2.read())

        inb = [s.strip() for s in inbound.split(",") if s.strip()]
        outb = [s.strip() for s in outbound.split(",") if s.strip()]
        nav = [s.strip() for s in navettaggio.split(",") if s.strip()]

        classify_flows(path, "database_classificato.xlsx", inb, outb, nav)
        st.success("✅ Script 2 completato.")
        st.download_button("⬇️ Scarica output Script 2", open("database_classificato.xlsx", "rb"), file_name="database_classificato.xlsx")

# === STEP 3 - DIMENSIONI + FASCE ===
elif menu == "Step 3 - Dimensioni / Fasce":
    st.header("📦 Step 3 - Dimensioni + Fasce di peso")
    if os.path.exists("database_classificato.xlsx"):
        if st.button("▶️ Esegui Script 3"):
            run_script3("database_classificato.xlsx", "database_dimensioni.xlsx")
            st.success("✅ Script 3 completato.")
            st.download_button("⬇️ Scarica output Script 3", open("database_dimensioni.xlsx", "rb"), file_name="database_dimensioni.xlsx")

        if os.path.exists("database_dimensioni.xlsx"):
            if os.path.exists("fasce di peso.xlsx"):
                if st.button("▶️ Esegui Script 4"):
                    run_script4("database_dimensioni.xlsx", "fasce di peso.xlsx", "database_fascia di peso.xlsx")
                    st.success("✅ Script 4 completato.")
                    st.download_button("⬇️ Scarica output Script 4", open("database_fascia di peso.xlsx", "rb"), file_name="database_fascia di peso.xlsx")
            else:
                st.error("❗ Manca il file 'fasce di peso.xlsx'. Caricalo nella directory principale del progetto.")

# === STEP 4 - GEOGRAFIA ===
elif menu == "Step 4 - Geografia":
    st.header("🌍 Step 4 - Arricchimento geografico")
    if os.path.exists("database_fascia di peso.xlsx"):
        if os.path.exists("geografia.xlsx"):
            if st.button("▶️ Esegui Script 5"):
                process_geography("database_fascia di peso.xlsx", "geografia.xlsx", "database arricchito con geografia.xlsx")
                st.success("✅ Script 5 completato.")
                st.download_button("⬇️ Scarica output Script 5", open("database arricchito con geografia.xlsx", "rb"), file_name="database_arricchito.xlsx")
        else:
            st.error("❗ Manca il file 'geografia.xlsx'. Caricalo nella directory principale del progetto.")

# === STEP 5 - FINALE ===
elif menu == "Step 5 - Finalizzazione":
    st.header("🎯 Step 5 - Finalizzazione e output finale")
    if os.path.exists("database arricchito con geografia.xlsx"):
        if st.button("▶️ Esegui Script 6"):
            run_script6()
            st.success("✅ Script finale completato.")
            st.download_button("⬇️ Scarica output finale", open("output_tratte_completo.xlsx", "rb"), file_name="output_tratte_completo.xlsx")
