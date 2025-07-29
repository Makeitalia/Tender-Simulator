import pandas as pd

def genera_prefisso(col_C, col_D, col_L, col_T):
    col_D = col_D.strip().lower()
    col_C = col_C.strip().lower()
    col_L = col_L.strip().lower()
    col_T = col_T.strip().lower()

    if col_D == 'inbound':
        X = 'I'
    elif col_D == 'outbound':
        X = 'O'
    elif col_D == 'navettaggio':
        X = 'N'
    else:
        return 'verificare'

    if col_C in ['marittimo-aereo']:
        Y = 'M'
    elif col_C == 'su ruota':
        if X == 'I' and col_L == 'italia':
            Y = 'I'
        elif X == 'O' and col_T == 'italia':
            Y = 'I'
        elif X == 'N' and col_L == 'italia' and col_T == 'italia':
            Y = 'I'
        else:
            Y = 'E'
    else:
        Y = 'E'

    return f"{X}{Y}"

def main():
    input_file = 'database arricchito con geografia.xlsx'
    df_raw = pd.read_excel(input_file, skiprows=2, header=None, dtype=str)

    # Filtra righe contenenti "verificare" in colonna D (3), I (8), Q (16)
    cols_to_check = [3, 8, 16]
    mask = df_raw[cols_to_check].apply(lambda x: ~x.astype(str).str.lower().str.contains("verificare", na=False), axis=1).all(axis=1)
    df_eliminate = df_raw[~mask]
    df_full = df_raw[mask]

    # Salva le righe escluse
    df_eliminate.to_excel("righe_eliminate.xlsx", index=False)

    # Salva debug righe escluse
    print(f"✅ Righe totali iniziali: {len(df_raw)}")
    print(f"❌ Righe eliminate: {len(df_eliminate)}")
    print(f"✅ Righe dopo pulizia: {len(df_full)}")

    # Continua come prima
    df = df_full.iloc[:, [2, 3, 7, 8, 9, 10, 11, 13, 15, 16, 17, 18, 19, 21, 26, 27, 31]].fillna('')
    df.columns = [
        'tipologia', 'flusso',
        'località origine', 'provincia/postal code', 'regione origine', 'rip. regioni origine', 'paese origine', 'continente origine',
        'località destinazione', 'provincia/postal code_dest', 'regione destinazione', 'rip. regioni destinazione', 'paese destinazione', 'continente destinazione',
        'peso_effettivo', 'fascia_peso', 'nolo'
    ]

    df['peso_effettivo'] = pd.to_numeric(df['peso_effettivo'], errors='coerce').fillna(0)
    df['nolo'] = pd.to_numeric(df['nolo'], errors='coerce').fillna(0)
    df.loc[df['tipologia'].isin(['aereo', 'marittimo']), 'tipologia'] = 'marittimo-aereo'

    codici = []
    verificare_count = 0
    prefisso_map = {}
    tratta_counter = {}
    tratta_fasce_counter = {}
    tratta_fasce_peso = {}
    tratta_fasce_nolo = {}

    for _, row in df.iterrows():
        c = row['tipologia']
        d = row['flusso']
        g = row['località origine']
        p_l = row['provincia/postal code']
        l = row['paese origine']
        o = row['località destinazione']
        p_t = row['provincia/postal code_dest']
        t = row['paese destinazione']
        fascia = row['fascia_peso']
        peso = row['peso_effettivo']
        nolo = row['nolo']

        if d.lower().strip() == 'verificare':
            codice = 'verificare'
            verificare_count += 1
        else:
            prefisso = genera_prefisso(c, d, l, t)
            if l.lower() == 'italia' and t.lower() == 'italia':
                key_origine = p_l.lower() if p_l else g.lower()
                key_destinazione = p_t.lower() if p_t else o.lower()
            else:
                key_origine = g.lower()
                key_destinazione = o.lower()

            tratta_key = (prefisso, key_origine, key_destinazione)

            if prefisso not in prefisso_map:
                prefisso_map[prefisso] = {}

            if tratta_key not in prefisso_map[prefisso]:
                nuovo_numero = len(prefisso_map[prefisso]) + 1
                codice_num = f"{nuovo_numero:03}"
                codice = f"{prefisso}_{codice_num}"
                prefisso_map[prefisso][tratta_key] = codice
            else:
                codice = prefisso_map[prefisso][tratta_key]

            tratta_counter[tratta_key] = tratta_counter.get(tratta_key, 0) + 1
            tratta_fasce_counter.setdefault(tratta_key, {})
            tratta_fasce_counter[tratta_key][fascia] = tratta_fasce_counter[tratta_key].get(fascia, 0) + 1
            tratta_fasce_peso.setdefault(tratta_key, {})
            tratta_fasce_peso[tratta_key][fascia] = tratta_fasce_peso[tratta_key].get(fascia, 0) + peso
            tratta_fasce_nolo.setdefault(tratta_key, {})
            tratta_fasce_nolo[tratta_key][fascia] = tratta_fasce_nolo[tratta_key].get(fascia, 0) + nolo

        codici.append(codice)

    df['ID tratta'] = codici

    for idx, row in df.iterrows():
        l = row['paese origine']
        t = row['paese destinazione']
        if l.lower().strip() == 'italia' and t.lower().strip() == 'italia':
            df.at[idx, 'località origine'] = ''
            df.at[idx, 'località destinazione'] = ''

    fasce_peso = [
        '<= 10 kg', '10 < kg <= 20', '20 < kg <= 50', '50 < kg <= 100', '100 < kg <= 200',
        '200 < kg <= 500', '500 < kg <= 1.000', '1.000 < kg <= 1.500', '1.500 < kg <= 2.500',
        '2.500 < kg <= 5.000', '5.000 < kg <= 10.000', '10.000< kg <= 15.000',
        '15.000< kg <= 20.000', '20.000< kg <= 24.000', '> 24.000 kg'
    ]

    def genera_df_finale(tratta_dizionario, col_totale_nome):
        righe_finali = []
        for tratta_key in tratta_counter:
            prefisso, key_origine, key_destinazione = tratta_key
            id_tratta = prefisso_map[prefisso][tratta_key]
            riga_esempio = df[df['ID tratta'] == id_tratta].iloc[0]
            riga_finale = riga_esempio.to_dict()
            conteggi_fasce = tratta_dizionario.get(tratta_key, {})
            for fascia in fasce_peso:
                riga_finale[fascia] = conteggi_fasce.get(fascia, 0)
            riga_finale[col_totale_nome] = sum(conteggi_fasce.values())
            righe_finali.append(riga_finale)
        return pd.DataFrame(righe_finali)

    def aggiungi_totali(df_finale, col_totale, label_totali):
        colonne_output = [
            'ID tratta', 'tipologia', 'flusso', 'località origine', 'provincia/postal code', 'regione origine',
            'rip. regioni origine', 'paese origine', 'continente origine',
            'località destinazione', 'provincia/postal code_dest', 'regione destinazione', 'rip. regioni destinazione',
            'paese destinazione', 'continente destinazione'
        ] + fasce_peso + [col_totale]
        df_finale = df_finale[colonne_output]
        df_finale = df_finale.sort_values(by='ID tratta').reset_index(drop=True)
        totali = {col: df_finale[col].sum() if col in fasce_peso + [col_totale] else '' for col in df_finale.columns}
        totali['ID tratta'] = label_totali
        df_finale = pd.concat([pd.DataFrame([totali]), df_finale], ignore_index=True)
        return df_finale

    df_frequenze = aggiungi_totali(genera_df_finale(tratta_fasce_counter, 'Numero_Trasporti'), 'Numero_Trasporti', 'totali frequenze')
    df_pesi = aggiungi_totali(genera_df_finale(tratta_fasce_peso, 'Peso_Totale'), 'Peso_Totale', 'totali peso')
    df_nolo = aggiungi_totali(genera_df_finale(tratta_fasce_nolo, 'Nolo_Totale'), 'Nolo_Totale', 'totali nolo')

    with pd.ExcelWriter("output_tratte_completo.xlsx", engine='openpyxl') as writer:
        df_frequenze.to_excel(writer, index=False, sheet_name='frequenze')
        df_pesi.to_excel(writer, index=False, sheet_name='peso')
        df_nolo.to_excel(writer, index=False, sheet_name='nolo')

    print("✅ File Excel creato: output_tratte_completo.xlsx")

if __name__ == '__main__':
    main()
