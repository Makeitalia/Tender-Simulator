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

# === Configurazione pagina ===
st.set_page_config(page_title="Workflow Analisi Dati", layout="wide")
st.title("📊 Workflow Analisi Dati - Tool Makeitalia")

upload_dir = "uploaded_files"
os.makedirs(upload_dir, exist_ok=True)

# === Menu laterale ===
menu = st.sidebar.selectbox("📁 Seleziona sezione", [
    "Home",
    "1. Flusso principale",
    "2. Analisi tempi (WIP)",
    "3. Report tratte (WIP)",
    "4. Cluster clienti (WIP)",
    "5. Ottimizzazione (WIP)"
])

# === HOME ===
if menu == "Home":
    st.header("ℹ️ Benvenuto nel Tool per Analisi Dati")
    st.markdown("""
    Questo strumento guida l'utente nell'esecuzione step-by-step di una serie di script per la pulizia e l'arricchimento dei dati logistici.

    ### ✅ Flusso supportato:
    - Pulizia iniziale
    - Classificazione flussi
    - Dimensioni e fasce
    - Geografia
    - Finalizzazione

    Tutti i file intermedi possono essere scaricati. Buon lavoro!
    """)

# === FLUSSO PRINCIPALE ===
elif menu == "1. Flusso principale":
    st.header("🛠 1. Flusso principale")

    # === Upload iniziale solo se mancano file ===
    if not os.path.exists("database_pulito.xlsx"):
        st.subheader("📂 Carica file di partenza")
        file1 = st.file_uploader("Carica file Excel iniziale", type="xlsx", key="iniziale")
        if file1:
            path_input = os.path.join(upload_dir, "input_file.xlsx")
            with open(path_input, "wb") as f:
                f.write(file1.read())
            clean_database_with_output(path_input, "database_pulito.xlsx", "righe_eliminate.xlsx")
            st.success("✅ Pulizia completata. File salvati come 'database_pulito.xlsx' e 'righe_eliminate.xlsx'")
            st.download_button("⬇️ Scarica righe eliminate", open("righe_eliminate.xlsx", "rb"), file_name="righe_eliminate.xlsx")

    # === Modifica opzionale dopo script 1 ===
    if os.path.exists("database_pulito.xlsx") and not os.path.exists("database_classificato.xlsx"):
        st.subheader("✏️ Vuoi modificare il file pulito?")
        st.download_button("⬇️ Scarica database pulito", open("database_pulito.xlsx", "rb"), file_name="database_pulito.xlsx")
        file_mod = st.file_uploader("Se sì, caricalo qui sopra (altrimenti prosegui)", type="xlsx", key="modifica1")
        file_to_use = "database_pulito_modificato.xlsx" if file_mod else "database_pulito.xlsx"

        if file_mod:
            with open(file_to_use, "wb") as f:
                f.write(file_mod.read())
            st.success("📥 File modificato caricato")

        # === Script 2: Classificazione
        st.markdown("---")
        st.subheader("▶️ Script 2: Classificazione flussi")
        inbound = st.text_input("Ragioni sociali INBOUND (virgola separati)")
        outbound = st.text_input("Ragioni sociali OUTBOUND (virgola separati)")
        navettaggio = st.text_input("Ragioni sociali NAVETTAGGIO (virgola separati)")
        if st.button("Esegui Script 2"):
            inb = [x.strip() for x in inbound.split(",") if x.strip()]
            outb = [x.strip() for x in outbound.split(",") if x.strip()]
            nav = [x.strip() for x in navettaggio.split(",") if x.strip()]
            classify_flows(file_to_use, "database_classificato.xlsx", inb, outb, nav)
            st.success("✅ Script 2 completato")
            st.download_button("⬇️ Scarica file classificato", open("database_classificato.xlsx", "rb"), file_name="database_classificato.xlsx")

    # === Script 3
    if os.path.exists("database_classificato.xlsx") and not os.path.exists("database_dimensioni.xlsx"):
        st.subheader("▶️ Script 3: Aggiunta dimensioni")
        if st.button("Esegui Script 3"):
            run_script3("database_classificato.xlsx", "database_dimensioni.xlsx")
            st.success("✅ Script 3 completato")
            st.download_button("⬇️ Scarica output", open("database_dimensioni.xlsx", "rb"), file_name="database_dimensioni.xlsx")

    # === Script 4
    if os.path.exists("database_dimensioni.xlsx") and not os.path.exists("database_fascia di peso.xlsx"):
        st.subheader("▶️ Script 4: Aggiunta fasce di peso")
        if not os.path.exists("fasce di peso.xlsx"):
            st.error("❗ Manca 'fasce di peso.xlsx'")
        elif st.button("Esegui Script 4"):
            run_script4("database_dimensioni.xlsx", "fasce di peso.xlsx", "database_fascia di peso.xlsx")
            st.success("✅ Script 4 completato")
            st.download_button("⬇️ Scarica output", open("database_fascia di peso.xlsx", "rb"), file_name="database_fascia_di_peso.xlsx")

    # === Script 5
    if os.path.exists("database_fascia di peso.xlsx") and not os.path.exists("database arricchito con geografia.xlsx"):
        st.subheader("▶️ Script 5: Geografia")
        if not os.path.exists("geografia.xlsx"):
            st.error("❗ Manca 'geografia.xlsx'")
        elif st.button("Esegui Script 5"):
            process_geography("database_fascia di peso.xlsx", "geografia.xlsx", "database arricchito con geografia.xlsx")
            st.success("✅ Script 5 completato")
            st.download_button("⬇️ Scarica output", open("database arricchito con geografia.xlsx", "rb"), file_name="database_arricchito.xlsx")

    # === Modifica opzionale dopo script 5 ===
    if os.path.exists("database arricchito con geografia.xlsx") and not os.path.exists("output_tratte_completo.xlsx"):
        st.subheader("✏️ Vuoi modificare il file geografico?")
        st.download_button("⬇️ Scarica file geografico", open("database arricchito con geografia.xlsx", "rb"), file_name="database_arricchito.xlsx")
        file_geo = st.file_uploader("Se sì, caricalo qui sopra (altrimenti prosegui)", type="xlsx", key="modifica2")
        path_geo_finale = "database_finale_modificato.xlsx" if file_geo else "database arricchito con geografia.xlsx"

        if file_geo:
            with open(path_geo_finale, "wb") as f:
                f.write(file_geo.read())
            st.success("📥 File modificato caricato")

        if st.button("🚀 Esegui Script 6 (finale)"):
            shutil.copy(path_geo_finale, "database arricchito con geografia.xlsx")
            run_script6()
            st.success("✅ Script 6 completato")
            st.download_button("⬇️ Scarica output finale", open("output_tratte_completo.xlsx", "rb"), file_name="output_tratte_completo.xlsx")

# === ALTRE SEZIONI WIP ===
else:
    st.header(f"🚧 {menu}")
    st.info("Questa sezione è in fase di sviluppo. Torna presto!")