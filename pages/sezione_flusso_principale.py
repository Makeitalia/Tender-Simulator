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

upload_dir = "uploaded_files"
os.makedirs(upload_dir, exist_ok=True)

st.set_page_config(page_title="Tender Simulator")
st.title("🛠️ Tender Simulator")

st.markdown("""
Benvenuto nel tool interattivo per l'analisi dei dati di tender.

**Cosa puoi fare:**
- Eseguire passo dopo passo il processo di pulizia, classificazione e arricchimento del database
- Scaricare i file intermedi per eventuali verifiche o modifiche
- Eseguire script in modo guidato, anche senza conoscenze tecniche

Usa il menu a sinistra per iniziare 👈
""")

if "fase" not in st.session_state:
    st.session_state.fase = 0

# === Sezione 1: Workflow principale ===
def run_flusso():
    st.header("🔄 Flusso Principale")

    # Step 1 - Upload file iniziale
    if st.session_state.fase == 0:
        st.subheader("Step 1: Carica file di partenza")
        uploaded_file = st.file_uploader("📂 Carica il file Excel da analizzare", type=["xlsx"])

        if uploaded_file:
            path_input = os.path.join(upload_dir, "input_file.xlsx")
            with open(path_input, "wb") as f:
                f.write(uploaded_file.read())

            output_clean = os.path.join(upload_dir, "database_pulito.xlsx")
            output_removed = os.path.join(upload_dir, "righe_eliminate.xlsx")

            clean_database_with_output(path_input, output_clean, output_removed)
            st.success("✅ File elaborato correttamente. Scarica i risultati o procedi.")

            st.download_button("📥 Scarica Database Pulito", open(output_clean, "rb"), file_name="database_pulito.xlsx")
            st.download_button("📥 Scarica Righe Eliminate", open(output_removed, "rb"), file_name="righe_eliminate.xlsx")

            if st.button("➡️ Avanti"):
                st.session_state.fase = 1
                st.rerun()

    # Step 2 - Eventuale modifica e classificazione
    elif st.session_state.fase == 1:
        st.subheader("Step 2: Verifica o modifica il database pulito")
        st.download_button("📥 Scarica Database Pulito", open(os.path.join(upload_dir, "database_pulito.xlsx"), "rb"), file_name="database_pulito.xlsx")
        file_modificato = st.file_uploader("🔧 Se hai modificato il file, ricaricalo qui", type="xlsx")

        if file_modificato:
            path_db = os.path.join(upload_dir, "database_pulito_modificato.xlsx")
            with open(path_db, "wb") as f:
                f.write(file_modificato.read())
        else:
            path_db = os.path.join(upload_dir, "database_pulito.xlsx")

        st.markdown("""
        🔹 Inserisci le RAGIONI SOCIALI per i tre tipi di flussi.
        """)
        inbound = st.text_input("Ragioni sociali INBOUND (separate da virgole)")
        outbound = st.text_input("Ragioni sociali OUTBOUND (separate da virgole)")
        nav = st.text_input("Ragioni sociali NAVETTAGGIO (separate da virgole)")

        if st.button("➡️ Esegui classificazione (Script 2)"):
            classify_flows(path_db, os.path.join(upload_dir, "database_classificato.xlsx"), inbound, outbound, nav)
            st.success("✅ Classificazione completata. Avanti al prossimo script.")
            st.session_state.fase = 2
            st.rerun()

    # Step 3 - Script 3 (dimensioni)
    elif st.session_state.fase == 2:
        st.subheader("Step 3: Calcolo dimensioni (Script 3)")
        run_script3(
            os.path.join(upload_dir, "database_classificato.xlsx"),
            os.path.join(upload_dir, "database_dimensioni.xlsx")
        )
        st.success("✅ Script 3 completato.")
        st.session_state.fase = 3
        st.rerun()

    # Step 4 - Script 4 (fasce di peso)
    elif st.session_state.fase == 3:
        st.subheader("Step 4: Fasce di peso (Script 4)")
        run_script4(
            os.path.join(upload_dir, "database_dimensioni.xlsx"),
            "fasce di peso.xlsx",
            os.path.join(upload_dir, "database_fascia di peso.xlsx")
        )
        st.success("✅ Script 4 completato.")
        st.session_state.fase = 4
        st.rerun()

    # Step 5 - Script 5 (geografia)
    elif st.session_state.fase == 4:
        st.subheader("Step 5: Geografia (Script 5)")
        geo_file = "geografia.xlsx"
        if not os.path.exists(geo_file):
            st.error("⚠️ Manca 'geografia.xlsx' nella cartella principale. Aggiungilo e ricarica.")
            st.stop()

        process_geography(
            os.path.join(upload_dir, "database_fascia di peso.xlsx"),
            geo_file,
            os.path.join(upload_dir, "database arricchito con geografia.xlsx")
        )
        st.success("✅ Script 5 completato.")
        st.session_state.fase = 5
        st.rerun()

    # Step 6 - Eventuale modifica + script finale
    elif st.session_state.fase == 5:
        st.subheader("Step 6: Modifica finale e script 6")
        st.download_button("📥 Scarica il file finale da modificare", open(os.path.join(upload_dir, "database arricchito con geografia.xlsx"), "rb"), file_name="database_arricchito.xlsx")
        file_finale = st.file_uploader("🔧 Se hai modificato il file, ricaricalo qui (altrimenti lascia vuoto)", type="xlsx")

        if file_finale:
            path_finale = os.path.join(upload_dir, "database_finale_modificato.xlsx")
            with open(path_finale, "wb") as f:
                f.write(file_finale.read())
        else:
            path_finale = os.path.join(upload_dir, "database arricchito con geografia.xlsx")

        if st.button("🚀 Esegui script finale (6)"):
            shutil.copy(path_finale, "database arricchito con geografia.xlsx")
            run_script6()
            st.success("✅ Workflow completato! Scarica i risultati dal file Excel generato.")
            st.session_state.fase = 6
            st.rerun()

    # Fine processo
    elif st.session_state.fase == 6:
        st.header("✅ Fine del processo")
        with open("output_tratte_completo.xlsx", "rb") as f:
            st.download_button("📥 Scarica output finale", f, file_name="output_tratte_completo.xlsx")
        if st.button("🔄 Ricomincia"):
            st.session_state.clear()
            st.rerun()

# Lancia la sezione 1
run_flusso()
