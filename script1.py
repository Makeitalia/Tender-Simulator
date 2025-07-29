import pandas as pd

def clean_database_with_output(file_path, output_path_clean, output_path_removed):
    # Carica il file Excel
    df = pd.read_excel(file_path, header=None)

    def transform_to_lowercase(value):
        if isinstance(value, str):
            return value.lower()
        return value

    # Trasforma tutti i valori in minuscolo
    df = df.applymap(transform_to_lowercase)

    # Colonne usate per i controlli
    column_N = df.columns[13]  # Colonna N
    column_R = df.columns[17]  # Colonna R
    column_S = df.columns[18]  # Colonna S
    col_G = df.columns[6]      # Colonna G
    col_K = df.columns[10]     # Colonna K
    col_W = df.columns[22]     # Colonna W
    col_U = df.columns[20]     # Colonna U
    col_V = df.columns[21]     # Colonna V

    def get_rejection_reason(row):
        tipologia = row[2]
        valid_tipologie = ['aereo', 'marittimo', 'su ruota']
        if tipologia not in valid_tipologie:
            return "Tipologia non valida"

        value_N = row[column_N]
        value_R = row[column_R]
        value_S = row[column_S]

        is_N_invalid = pd.isna(value_N) or not isinstance(value_N, (int, float))
        is_R_invalid = pd.isna(value_R) or not isinstance(value_R, (int, float))
        is_S_invalid = pd.isna(value_S) or not isinstance(value_S, (int, float))

        are_all_zero = (value_N == 0 if isinstance(value_N, (int, float)) else False) and \
                       (value_R == 0 if isinstance(value_R, (int, float)) else False) and \
                       (value_S == 0 if isinstance(value_S, (int, float)) else False)

        exceeds_max_values = (
            (isinstance(value_N, (int, float)) and value_N > 33000) or
            (isinstance(value_R, (int, float)) and value_R > 100) or
            (isinstance(value_S, (int, float)) and value_S > 33000)
        )

        base_dimension_check = not (
            (is_N_invalid and is_R_invalid and is_S_invalid) or
            are_all_zero or
            exceeds_max_values
        )

        if tipologia == "marittimo" and not base_dimension_check:
            value_U = row[col_U]
            value_V = row[col_V]
            u_ok = isinstance(value_U, (int, float)) and value_U >= 1
            v_ok = isinstance(value_V, (int, float)) and value_V >= 1
            if not (u_ok or v_ok):
                return "Dimensioni non valide nelle colonne N/R/S. possibile presenza di lettere, valori nulli o maggiori del limite consentitto"
        elif not base_dimension_check:
            return "Dimensioni non valide nelle colonne N/R/S. possibile presenza di lettere, valori nulli o maggiori del limite consentitto"

        g_is_empty = pd.isna(row[col_G]) or str(row[col_G]).strip() == ''
        k_is_empty = pd.isna(row[col_K]) or str(row[col_K]).strip() == ''
        if g_is_empty or k_is_empty:
            return "Mancano i dati relativi all'origine o alla destinazione"

        value_W = row[col_W]
        is_W_valid = isinstance(value_W, (int, float)) and not pd.isna(value_W) and value_W != 0
        if not is_W_valid:
            return "Manca il valore del nolo as-is"

        return None  # Nessun errore → riga valida

    # Mantieni le prime due righe originali
    first_two_rows = df.iloc[:2].copy()
    rows_to_filter = df.iloc[2:]

    # Valuta ciascuna riga
    rejection_reasons = rows_to_filter.apply(get_rejection_reason, axis=1)

    # Maschera righe valide/da scartare
    mask_valid = rejection_reasons.isna()
    filtered_rows = rows_to_filter[mask_valid]
    removed_rows = rows_to_filter[~mask_valid].copy()

    # === DATABASE PULITO ===
    df_filtered = pd.concat([first_two_rows, filtered_rows])

    # === RIGHE ELIMINATE ===
    # Aggiungi la colonna "Motivo scarto" solo alle righe eliminate
    removed_rows.insert(27, "Motivo scarto", rejection_reasons[~mask_valid])

    # Crea una copia delle prime due righe e aggiungi colonna vuota + intestazione
    first_two_removed = first_two_rows.copy()
    first_two_removed.insert(27, "Motivo scarto", ["", "Motivo scarto"])

    # Combina intestazione + righe eliminate
    removed_with_header = pd.concat([first_two_removed, removed_rows])

    # === SALVATAGGIO ===
    df_filtered.to_excel(output_path_clean, index=False, header=False)
    removed_with_header.to_excel(output_path_removed, index=False, header=False)

    # Log finale
    print(f"Numero di righe eliminate: {len(removed_rows)}")
    print(f"File pulito salvato in: {output_path_clean}")
    print(f"Righe eliminate salvate in: {output_path_removed}")


# ===== ESEMPIO DI UTILIZZO =====

input_file = "Database Test.xlsx"
output_clean = "database_pulito.xlsx"
output_removed = "righe_eliminate.xlsx"

clean_database_with_output(input_file, output_clean, output_removed)
