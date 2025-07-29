import pandas as pd

def calculate_max_dimension(df, col_P, col_Q, col_R):
    def max_dim(row):
        values = [row[col_P], row[col_Q], row[col_R]]
        cleaned = []
        for val in values:
            if pd.isna(val):
                continue
            elif isinstance(val, (int, float)):
                cleaned.append(val)
            else:
                return "verificare"
        if not cleaned:
            return ""
        return max(cleaned)

    return df.apply(max_dim, axis=1)

def calculate_peso_volumetrico(df, volume_col_index):
    def peso_vol(row):
        value = row[volume_col_index]
        if pd.isna(value):
            return ""
        elif isinstance(value, (int, float)):
            return round(value * 333, 2)
        else:
            return "verificare"

    return df.apply(peso_vol, axis=1)

# Esempio di utilizzo
file_path = "database_classificato.xlsx"
output_path = "database_dimensioni.xlsx"

df = pd.read_excel(file_path, header=None)

# Calcola max dimensione (colonne O=15, P=16, Q=17)
df.insert(18, "max_dimensione", "")
df.iloc[1, 18] = "max_dimensione"
df.iloc[2:, 18] = calculate_max_dimension(df.iloc[2:], 15, 16, 17)

# Elimina colonne O, P, Q (indici 15,16,17)
df.drop(df.columns[[15, 16, 17]], axis=1, inplace=True)

# 🔥 Ricalcola gli indici delle colonne
df.columns = range(df.shape[1])

# Ora puoi usare direttamente gli indici "fisici"
volume_col_index = 16
peso_volumetrico_index = 17

df.insert(peso_volumetrico_index, "peso volumetrico [kg]", "")
df.iloc[1, peso_volumetrico_index] = "peso volumetrico [kg]"
df.iloc[2:, peso_volumetrico_index] = calculate_peso_volumetrico(df.iloc[2:], volume_col_index)

df.to_excel(output_path, index=False, header=False)
print("Calcolo completato e file salvato!")