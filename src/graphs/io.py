"""
io.py — carregar/validar o CSV fornecido
"""
import pandas as pd
import os

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