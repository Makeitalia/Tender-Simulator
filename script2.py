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

def classify_flows(file_path, output_path, inbound_rag, outbound_rag, nav_rag):
    df = pd.read_excel(file_path, header=None)

    inbound_rag = [normalize(r) for r in inbound_rag]
    outbound_rag = [normalize(r) for r in outbound_rag]
    nav_rag = [normalize(r) for r in nav_rag]

    col_F = 6
    col_J = 10

    df.insert(3, "flusso", "")
    df.iloc[1, 3] = "flusso"

    for i in range(2, len(df)):
        val_F = normalize(df.iat[i, col_F]) if not pd.isna(df.iat[i, col_F]) else ""
        val_J = normalize(df.iat[i, col_J]) if not pd.isna(df.iat[i, col_J]) else ""

        inbound_match = any(r in val_J for r in inbound_rag) and not any(r in val_F for r in inbound_rag)
        outbound_match = any(r in val_F for r in outbound_rag) and not any(r in val_J for r in outbound_rag)

        nav_f = [r for r in nav_rag if r in val_F]
        nav_j = [r for r in nav_rag if r in val_J]
        nav_match = nav_f and nav_j and not any(f == j for f in nav_f for j in nav_j)

        if inbound_match:
            df.iat[i, 3] = "inbound"
        elif outbound_match:
            df.iat[i, 3] = "outbound"
        elif nav_match:
            df.iat[i, 3] = "navettaggio"
        else:
            df.iat[i, 3] = "verificare"

    df.to_excel(output_path, index=False, header=False)
