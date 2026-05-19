"""
io.py — carregar/validar o CSV fornecido
"""
import pandas as pd
import os


def carregar_grafo(caminho_aeroportos: str, caminho_adjacencias: str):
    from graphs.graph import Grafo

    df = carregar_aeroportos(caminho_aeroportos)

    if not os.path.exists(caminho_adjacencias):
        raise FileNotFoundError(f"Arquivo de adjacências não encontrado: {caminho_adjacencias}")

    df_adj = pd.read_csv(caminho_adjacencias)
    for col in ('origem', 'destino', 'peso'):
        if col not in df_adj.columns:
            raise ValueError(f"Coluna obrigatória '{col}' ausente em adjacencias.")

    grafo = Grafo()
    for _, row in df.iterrows():
        grafo.adicionar_vertice(row['iata'], {'cidade': row['cidade'], 'regiao': row['regiao']})

    for _, row in df_adj.iterrows():
        grafo.adicionar_aresta(row['origem'], row['destino'], row['peso'])

    return grafo, df


def carregar_aeroportos(caminho_arquivo: str) -> pd.DataFrame:
    """
    Carrega e valida o arquivo de dados dos aeroportos.
    """
    # 1. Verificação de Segurança: O arquivo existe?
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Erro Crítico: O arquivo {caminho_arquivo} não foi encontrado.")

    try:
        # 2. Leitura
        df = pd.read_csv(caminho_arquivo)

        # 3. Validação de Colunas (Schema)
        colunas_obrigatorias = ['iata', 'cidade', 'regiao']
        for col in colunas_obrigatorias:
            if col not in df.columns:
                raise ValueError(f"Erro de Formato: Coluna obrigatória '{col}' ausente no CSV.")

        # 4. Limpeza de Dados (Sanitização)
        # Remove espaços vazios acidentais e garante IATA em caixa alta
        df['iata'] = df['iata'].str.strip().str.upper()
        df['regiao'] = df['regiao'].str.strip()
        
        return df

    except Exception as e:
        print(f"Erro inesperado ao ler os dados: {e}")
        raise