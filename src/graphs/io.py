import pandas as pd

def carregar_aeroportos(caminho_csv):
    df = pd.read_csv(caminho_csv)

    df['iata'] = df['iata'].str.strip().str.upper()
    
    return df.to_dict('records')