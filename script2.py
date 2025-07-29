import pandas as pd
import unicodedata
import re

def normalize(text):
    if not isinstance(text, str):
        return ''
    text = unicodedata.normalize('NFKD', text)
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

def classify_flows(file_path, output_path):
    df = pd.read_excel(file_path, header=None)

    # === INPUT con istruzioni chiare ===
    print("\n🔹 Inserisci le RAGIONI SOCIALI per classificare i flussi INBOUND.")
    print("   👉 Devono essere presenti nella COLONNA J ma non nella COLONNA F.")
    print("   ✅ Scrivi i nomi separati da virgola, ad esempio:\n   acme spa, stabilimento torino, logistica nord")
    inbound_input = input("   ✏️  Inserisci ragioni sociali inbound: ")
    inbound_rag = [normalize(r.strip()) for r in inbound_input.split(",") if r.strip()]

    print("\n🔹 Inserisci le RAGIONI SOCIALI per classificare i flussi OUTBOUND.")
    print("   👉 Devono essere presenti nella COLONNA F ma non nella COLONNA J.")
    print("   ✅ Scrivi i nomi separati da virgola, ad esempio:\n   zara, logistica roma, centro smistamento")
    outbound_input = input("   ✏️  Inserisci ragioni sociali outbound: ")
    outbound_rag = [normalize(r.strip()) for r in outbound_input.split(",") if r.strip()]

    print("\n🔹 Inserisci le RAGIONI SOCIALI per classificare i flussi NAVETTAGGIO.")
    print("   👉 Una deve essere in COLONNA F e un'altra diversa in COLONNA J.")
    print("   ❗ Se la stessa appare in entrambe, verrà classificata come 'verificare'.")
    print("   ✅ Scrivi un solo elenco, separato da virgole, ad esempio:\n   magazzino, stabilimento, deposito")
    nav_input = input("   ✏️  Inserisci ragioni sociali navettaggio: ")
    nav_rag = [normalize(r.strip()) for r in nav_input.split(",") if r.strip()]

    if not (inbound_rag or outbound_rag or nav_rag):
        print("\n❌ Nessuna ragione sociale valida inserita. Interrompo l'esecuzione.")
        return

    # === Colonne di interesse ===
    col_F = 6   # colonna F = origine
    col_J = 10  # colonna J = destinazione

    # Inserisci colonna "flusso" tra C e D (posizione 3)
    df.insert(3, "flusso", "")
    df.iloc[1, 3] = "flusso"

    # === Classificazione ===
    for i in range(2, len(df)):
        val_F = normalize(df.iat[i, col_F]) if not pd.isna(df.iat[i, col_F]) else ""
        val_J = normalize(df.iat[i, col_J]) if not pd.isna(df.iat[i, col_J]) else ""

        # INBOUND: match in J ma non in F
        inbound_match = any(rag in val_J for rag in inbound_rag) and not any(rag in val_F for rag in inbound_rag)

        # OUTBOUND: match in F ma non in J
        outbound_match = any(rag in val_F for rag in outbound_rag) and not any(rag in val_J for rag in outbound_rag)

        # NAVETTAGGIO: almeno una ragione in F e una diversa in J
        nav_f_matches = [rag for rag in nav_rag if rag in val_F]
        nav_j_matches = [rag for rag in nav_rag if rag in val_J]
        navettaggio_match = False

        if nav_f_matches and nav_j_matches:
            # Verifica che siano diverse
            if not any(f == j for f in nav_f_matches for j in nav_j_matches):
                navettaggio_match = True

        # Assegna classificazione
        if inbound_match:
            df.iat[i, 3] = "inbound"
        elif outbound_match:
            df.iat[i, 3] = "outbound"
        elif navettaggio_match:
            df.iat[i, 3] = "navettaggio"
        else:
            df.iat[i, 3] = "verificare"

    # === Salvataggio ===
    df.to_excel(output_path, index=False, header=False)
    print(f"\n✅ File elaborato e salvato in: {output_path}")

# === ESEMPIO DI UTILIZZO ===
input_file = "database_pulito.xlsx"
output_file = "database_classificato.xlsx"

classify_flows(input_file, output_file)