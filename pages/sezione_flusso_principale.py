import streamlit as st
import os
import pandas as pd
import shutil

from script1 import clean_database_with_output
from script2 import classify_flows
from script3 import run_script3
from script4 import run_script4
from script5 import process_geography
from script6 import main as run_script6


def run():
    st.header("🛠 Flusso principale")

    if "fase" not in st.session_state:
        st.session_state.fase = 0

    upload_dir = "uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)

    # === Fase 0: Caricamento file iniziale ===
    if st.session_state.fase == 0:
        st.subheader("Step 1: Carica file iniziale")
        uploaded_file = st.file_uploader("📂 Carica il file Excel da analizzare", type=["xlsx"])

        if uploaded_file:
            path_input = os.path.join(upload_dir, "input_file.xlsx")
            with open(path_input, "wb") as f:
                f.write(uploaded_file.read())

            output_clean = os.path.join(upload_dir, "database_pulito.xlsx")
            output_removed = os.path.join(upload_dir, "righe_eliminate.xlsx")

            clean_database_with_output(path_input, output_clean, output_removed)

            st.success("✅ File pulito generato.")
            st.download_button("📥 Scarica righe eliminate", open(output_removed, "rb"), file_name="righe_eliminate.xlsx")

            st.session_state.fase = 1
            st.rerun()

    # === Fase 1: Modifica facoltativa ===
    elif st.session_state.fase == 1:
        st.subheader("Step 2: Modifica opzionale file pulito")

        st.download_button("📥 Scarica Database Pulito", open(os.path.join(upload_dir, "database_pulito.xlsx"), "rb"), file_name="database_pulito.xlsx")
        file_modificato = st.file_uploader("🔧 Se hai modificato il file, caricalo qui", type="xlsx")

        if file_modificato:
            path_db = os.path.join(upload_dir, "database_pulito_modificato.xlsx")
            with open(path_db, "wb") as f:
                f.write(file_modificato.read())
        else:
            path_db = os.path.join(upload_dir, "database_pulito.xlsx")

        if st.button("➡️ Procedi con script 2"):
            st.session_state.path_db_corrente = path_db
            st.session_state.fase = 2
            st.rerun()

    # === Fase 2: Script 2 ===
    elif st.session_state.fase == 2:
        st.subheader("Step 3: Classificazione flussi")

        col1, col2, col3 = st.columns(3)
        with col1:
            inbound = st.text_input("Ragioni sociali INBOUND")
        with col2:
            outbound = st.text_input("Ragioni sociali OUTBOUND")
        with col3:
            nav = st.text_input("Ragioni sociali NAVETTAGGIO")

        if st.button("➡️ Esegui Script 2"):
            classify_flows(
                st.session_state.path_db_corrente,
                os.path.join(upload_dir, "database_classificato.xlsx"),
                inbound, outbound, nav
            )
            st.success("✅ Flussi classificati.")
            st.session_state.fase = 3
            st.rerun()

    # === Fase 3: Script 3 ===
    elif st.session_state.fase == 3:
        st.subheader("Step 4: Calcolo dimensioni")
        if st.button("➡️ Esegui Script 3"):
            run_script3(
                os.path.join(upload_dir, "database_classificato.xlsx"),
                os.path.join(upload_dir, "database_dimensioni.xlsx")
            )
            st.success("✅ Dimensioni calcolate.")
            st.session_state.fase = 4
            st.rerun()

    # === Fase 4: Script 4 ===
    elif st.session_state.fase == 4:
        st.subheader("Step 5: Calcolo fascia di peso")
        if st.button("➡️ Esegui Script 4"):
            run_script4(
                os.path.join(upload_dir, "database_dimensioni.xlsx"),
                os.path.join(upload_dir, "database_fascia di peso.xlsx")
            )
            st.success("✅ Fasce calcolate.")
            st.session_state.fase = 5
            st.rerun()

    # === Fase 5: Script 5 (geografia) ===
    elif st.session_state.fase == 5:
        st.subheader("Step 6: Aggiunta geografia")

        fasce_ok = os.path.exists("fasce di peso.xlsx")
        geo_ok = os.path.exists("geografia.xlsx")
        if not (fasce_ok and geo_ok):
            st.error("⚠️ Manca 'fasce di peso.xlsx' o 'geografia.xlsx'.")
            return

        if st.button("➡️ Esegui Script 5"):
            process_geography(
                os.path.join(upload_dir, "database_fascia di peso.xlsx"),
                "geografia.xlsx",
                os.path.join(upload_dir, "database arricchito con geografia.xlsx")
            )
            st.success("✅ Geografia aggiunta.")
            st.session_state.fase = 6
            st.rerun()

    # === Fase 6: Modifica opzionale ===
    elif st.session_state.fase == 6:
        st.subheader("Step 7: Modifica opzionale prima dello script finale")
        st.download_button("📥 Scarica file da verificare", open(os.path.join(upload_dir, "database arricchito con geografia.xlsx"), "rb"), file_name="database_arricchito.xlsx")

        file_finale = st.file_uploader("🔧 Se hai modificato il file, ricaricalo qui", type="xlsx")

        if file_finale:
            path_finale = os.path.join(upload_dir, "database_finale_modificato.xlsx")
            with open(path_finale, "wb") as f:
                f.write(file_finale.read())
        else:
            path_finale = os.path.join(upload_dir, "database arricchito with geografia.xlsx")

        if st.button("🚀 Esegui script finale"):
            shutil.copy(path_finale, "database arricchito with geografia.xlsx")
            run_script6()
            st.session_state.fase = 7
            st.success("✅ Tutto completato!")
            st.rerun()

    # === Fase 7: Fine ===
    elif st.session_state.fase == 7:
        st.subheader("🎉 Fine processo")
        with open("output_tratte_completo.xlsx", "rb") as f:
            st.download_button("📥 Scarica output finale", f, file_name="output_tratte_completo.xlsx")
        if st.button("🔄 Ricomincia" ):
            st.session_state.clear()
            st.rerun()