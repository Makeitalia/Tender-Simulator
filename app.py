import streamlit as st
import os
import pandas as pd
import shutil

from script1 import clean_database_with_output
from script2 import classify_flows
from script3 import run_script3  # Wrapper che esegue 03
from script4 import run_script4  # Wrapper che esegue 04
from script5 import process_geography
from script6 import main as run_script6  # Script finale

# === Setup iniziale ===
st.set_page_config(page_title="Workflow Analisi Dati", layout="centered")
st.title("🧩 Workflow Analisi Dati")

# === Stato di sessione ===
if "fase" not in st.session_state:
    st.session_state.fase = 0

upload_dir = "uploaded_files"
os.makedirs(upload_dir, exist_ok=True)

# === Fase 0: Upload file iniziale ===
if st.session_state.fase == 0:
    st.header("Step 1: Carica file di partenza")
    file_iniziale = st.file_uploader("📂 Carica il file Excel da analizzare", type="xlsx")

    if file_iniziale:
        path_input = os.path.join(upload_dir, "input_originale.xlsx")
        with open(path_input, "wb") as f:
            f.write(file_iniziale.read())

        st.success("✅ File caricato correttamente.")

        output_clean = os.path.join(upload_dir, "database_pulito.xlsx")
        output_removed = os.path.join(upload_dir, "righe_eliminate.xlsx")

        clean_database_with_output(path_input, output_clean, output_removed)
        st.session_state.fase = 1
        st.rerun()

# === Fase 1: Caricamento opzionale di versione modificata ===
elif st.session_state.fase == 1:
    st.header("Step 2: Verifica o modifica il database pulito")
    st.download_button("📥 Scarica Database Pulito", open(os.path.join(upload_dir, "database_pulito.xlsx"), "rb"), file_name="database_pulito.xlsx")
    file_modificato = st.file_uploader("🔧 Se hai modificato il file, ricaricalo qui (altrimenti lascia vuoto)", type="xlsx")

    if file_modificato:
        path_db = os.path.join(upload_dir, "database_pulito_modificato.xlsx")
        with open(path_db, "wb") as f:
            f.write(file_modificato.read())
    else:
        path_db = os.path.join(upload_dir, "database_pulito.xlsx")

    if st.button("➡️ Procedi con lo script 2-5"):
        classify_flows(path_db, os.path.join(upload_dir, "database_classificato.xlsx"))
        run_script3(os.path.join(upload_dir, "database_classificato.xlsx"), os.path.join(upload_dir, "database_dimensioni.xlsx"))
        run_script4(os.path.join(upload_dir, "database_dimensioni.xlsx"), os.path.join(upload_dir, "database_fascia di peso.xlsx"))

        fasce_ok = os.path.exists("fasce di peso.xlsx")
        geo_ok = os.path.exists("geografia.xlsx")
        if not (fasce_ok and geo_ok):
            st.error("⚠️ Manca 'fasce di peso.xlsx' o 'geografia.xlsx' nella cartella principale. Aggiungili e ricarica l'app.")
            st.stop()

        process_geography(
            os.path.join(upload_dir, "database_fascia di peso.xlsx"),
            "geografia.xlsx",
            os.path.join(upload_dir, "database arricchito con geografia.xlsx")
        )
        st.session_state.fase = 2
        st.rerun()

# === Fase 2: Modifica finale opzionale ===
elif st.session_state.fase == 2:
    st.header("Step 3: Modifica finale opzionale")
    st.download_button("📥 Scarica il file finale da modificare", open(os.path.join(upload_dir, "database arricchito con geografia.xlsx"), "rb"), file_name="database_arricchito.xlsx")
    file_finale = st.file_uploader("🔧 Se hai modificato il file, ricaricalo qui (altrimenti lascia vuoto)", type="xlsx")

    if file_finale:
        path_finale = os.path.join(upload_dir, "database_finale_modificato.xlsx")
        with open(path_finale, "wb") as f:
            f.write(file_finale.read())
    else:
        path_finale = os.path.join(upload_dir, "database arricchito con geografia.xlsx")

    if st.button("🚀 Esegui script finale"):
        shutil.copy(path_finale, "database arricchito con geografia.xlsx")
        run_script6()
        st.success("✅ Workflow completato! Scarica i risultati dal file Excel generato.")
        st.session_state.fase = 3

# === Fase 3: Fine ===
elif st.session_state.fase == 3:
    st.header("✅ Fine del processo")
    with open("output_tratte_completo.xlsx", "rb") as f:
        st.download_button("📥 Scarica output finale", f, file_name="output_tratte_completo.xlsx")
    if st.button("🔄 Ricomincia" ):
        st.session_state.clear()
        st.rerun()
