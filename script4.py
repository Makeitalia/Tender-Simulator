import pandas as pd

# Percorsi file
input_file = "database_dimensioni.xlsx"
fasce_file = "fasce di peso.xlsx"
output_file = "database_fascia di peso.xlsx"

# Leggi tutto il file principale come "raw"
df_all = pd.read_excel(input_file, header=None)

# Indici delle colonne
col_peso_reale_index = 14
col_peso_volumetrico_index = 17
col_peso_tassabile_index = 18

# Leggi le fasce di peso, usando la prima riga come intestazione (header=0)
fasce_df = pd.read_excel(fasce_file, header=0)
# Colonna 0: nome fascia, colonna 1: min, colonna 2: max
fasce = fasce_df.values.tolist()

# Aggiungi la colonna "fascia di peso" a destra della colonna "peso tassabile [kg]"
df_all.insert(col_peso_tassabile_index + 1, "fascia di peso", "")

# Aggiungi l'intestazione "fascia di peso" nella riga 1 (indice 1)
df_all.iat[1, col_peso_tassabile_index + 1] = "fascia di peso"

def is_num(val):
    try:
        float(val)
        return True
    except:
        return False

def trova_fascia(peso):
    try:
        peso_float = float(peso)
    except:
        return ""  # Se non numerico, vuoto

    for nome, min_val, max_val in fasce:
        if peso_float > min_val and peso_float <= max_val:
            return nome
    return ""  # Se non cade in nessuna fascia

# Applica la logica solo dalla riga 2 in poi (escludendo le prime due)
for idx in range(2, len(df_all)):
    row = df_all.iloc[idx]

    # CALCOLO PESO TASSABILE
    peso_tassabile = row[col_peso_tassabile_index]
    if not (isinstance(peso_tassabile, (int, float)) and not pd.isna(peso_tassabile)):
        val_14 = str(row[col_peso_reale_index]).strip() if not pd.isna(row[col_peso_reale_index]) else ""
        val_17 = str(row[col_peso_volumetrico_index]).strip() if not pd.isna(row[col_peso_volumetrico_index]) else ""
        val_14 = val_14.replace(",", ".")
        val_17 = val_17.replace(",", ".")

        numerici = [float(v) for v in [val_14, val_17] if is_num(v)]
        if len(numerici) == 2:
            peso_tassabile = max(numerici)
        elif len(numerici) == 1:
            peso_tassabile = numerici[0]
        else:
            if "verificare" in val_14.lower() or "verificare" in val_17.lower():
                peso_tassabile = "verificare"
            elif val_14 in ["", "-"] and val_17 in ["", "-"]:
                peso_tassabile = "verificare"
            else:
                peso_tassabile = "verificare"

        # Aggiorna la colonna "peso tassabile [kg]"
        df_all.iat[idx, col_peso_tassabile_index] = peso_tassabile

    # CALCOLO FASCIA DI PESO
    fascia_nome = trova_fascia(peso_tassabile)
    df_all.iat[idx, col_peso_tassabile_index + 1] = fascia_nome

# Salva tutto, intatto
df_all.to_excel(output_file, index=False, header=False)
print("✅ File finale creato con la colonna 'fascia di peso' e 'peso tassabile [kg]' aggiornato!")