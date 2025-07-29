import pandas as pd
import unicodedata
import re

def normalize(text):
    if not isinstance(text, str):
        return ''
    text = unicodedata.normalize('NFKD', text)
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

def process_geography(file_path, reference_file_path, output_path):
    df = pd.read_excel(file_path, header=None)
    reference_df = pd.read_excel(reference_file_path, sheet_name=None)
    geo_df = reference_df[list(reference_df.keys())[0]]
    continent_df = reference_df[list(reference_df.keys())[1]]
    postal_df = reference_df[list(reference_df.keys())[2]]

    lookup_col3 = {normalize(str(row[2])): row[1] for _, row in postal_df.iterrows() if not pd.isna(row[2])}
    lookup_col5 = {normalize(str(row[4])): row[1] for _, row in postal_df.iterrows() if not pd.isna(row[4])}
    lookup_col4 = {normalize(str(row[3])): row[1] for _, row in postal_df.iterrows() if not pd.isna(row[3])}

    column_H_index = 7
    column_I_index = 11
    column_L_index = 15
    column_M_index = 19
    dest_insert_pos = 16

    df.insert(8, "provincia/postal code", "")
    df.insert(9, "regione", "")
    df.insert(10, "ripartizione regioni", "")
    df.iloc[1, 8] = "provincia/postal code"
    df.iloc[1, 9] = "regione"
    df.iloc[1, 10] = "ripartizione regioni"

    df.insert(13, "continente", "")
    df.iloc[1, 13] = "continente"

    df.insert(dest_insert_pos, "provincia/postal code_dest", "")
    df.insert(dest_insert_pos + 1, "regione_dest", "")
    df.insert(dest_insert_pos + 2, "ripartizione regioni_dest", "")
    df.iloc[1, dest_insert_pos] = "provincia/postal code_dest"
    df.iloc[1, dest_insert_pos + 1] = "regione_dest"
    df.iloc[1, dest_insert_pos + 2] = "ripartizione regioni_dest"

    df.insert(21, "continente_dest", "")
    df.iloc[1, 21] = "continente_dest"

    synonyms = {
        "uk": "regno unito",
        "usa": "stati uniti",
        "rep. dominicana": "repubblica dominicana",
        "new zeland": "new zealand",
        "emirati arabi": "emirati arabi uniti",
        "corea del sud": "repubblica di corea",
        "costa avorio": "costa d'avorio"
    }

    def get_postal_code(locality, country):
        val_loc = normalize(locality)
        val_country = normalize(country)
        if val_loc == val_country:
            return "verificare"
        if val_loc in lookup_col3:
            return f"{lookup_col3[val_loc]}, {locality}"
        if val_loc in lookup_col5:
            return f"{lookup_col5[val_loc]}, {locality}"
        if val_loc in lookup_col4:
            return f"{lookup_col4[val_loc]}, {locality}"
        return "verificare"

    def populate_origin_fields(row):
        country = row.iloc[column_I_index]
        locality = row.iloc[column_H_index]
        if normalize(str(country)) == "italia":
            match = geo_df[geo_df.iloc[:, 0] == locality]
            if not match.empty:
                return pd.Series([match.iloc[0, 1], match.iloc[0, 2], match.iloc[0, 3]])
            else:
                return pd.Series(["verificare"] * 3)
        else:
            postal = get_postal_code(locality, country)
            return pd.Series([postal, "", ""])

    def populate_destination_fields(row):
        country = row.iloc[column_M_index]
        locality = row.iloc[column_L_index]
        if normalize(str(country)) == "italia":
            match = geo_df[geo_df.iloc[:, 0] == locality]
            if not match.empty:
                return pd.Series([match.iloc[0, 1], match.iloc[0, 2], match.iloc[0, 3]])
            else:
                return pd.Series(["verificare"] * 3)
        else:
            postal = get_postal_code(locality, country)
            return pd.Series([postal, "", ""])

    def get_continent(country):
        if pd.isna(country):
            return "verificare"
        mapped_country = synonyms.get(country.strip().lower(), country)
        norm_country = normalize(mapped_country)
        for idx, row in continent_df.iterrows():
            for i in range(5):
                ref = normalize(row[i])
                if norm_country == ref:
                    cont = row[5]
                    if pd.isna(cont) or cont == "":
                        return "verificare"
                    return cont
        return "verificare"

    df.iloc[2:, [8, 9, 10]] = df.iloc[2:].apply(populate_origin_fields, axis=1)
    df.iloc[2:, [dest_insert_pos, dest_insert_pos + 1, dest_insert_pos + 2]] = \
        df.iloc[2:].apply(populate_destination_fields, axis=1)

    for i in range(2, len(df)):
        country_orig = df.iat[i, column_I_index]
        country_dest = df.iat[i, column_M_index]
        df.iat[i, 13] = get_continent(country_orig)
        df.iat[i, 21] = get_continent(country_dest)

    df.to_excel(output_path, index=False, header=False)
    print(f"✅ File geografico generato: {output_path}")

# === Protezione per evitare esecuzione automatica su Streamlit ===
if __name__ == "__main__":
    input_file = "database_fascia di peso.xlsx"
    reference_file = "geografia.xlsx"
    output_file = "database arricchito con geografia.xlsx"
    process_geography(input_file, reference_file, output_file)