"""
io.py — carregar/validar o CSV fornecido
"""
import pandas as pd
import os

from graphs.graph import Grafo

def carregar_grafo(caminho_aeroportos: str, caminho_adjacencias: str):
    """
    Constroi um Grafo a partir de aeroportos_data.csv e adjacencias_aeroportos.csv.
    """

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

def carregar_e_validar_elencos(caminho_csv):
    """
    Lê o CSV, valida a estrutura das colunas (precisa ter 12) 
    e retorna uma lista contendo os elencos (listas de atores).
    """
    todos_os_elencos = []
    
    # O pd.read_csv já sabe ler direto do caminho (string), não precisa do 'with open'
    df = pd.read_csv(caminho_csv)
    
    # Validação do shape: se o DataFrame não tiver 12 colunas no total, o arquivo está errado
    # df.shape[1] nos dá o número de colunas
    if df.shape[1] != 12:
        print(f"[Aviso] O arquivo possui {df.shape[1]} colunas em vez de 12. Verifique o dataset!")
        # Dependendo do rigor, você pode dar um return vazio ou um raise aqui.
    
    # Iterando pelas linhas do DataFrame do jeito correto no Pandas
    # O index começa em 0, somamos +2 para dar o número real da linha no arquivo físico
    for index, linha in df.iterrows():
        num_linha = index + 2 
        
        # Acessamos a coluna 'cast' de forma segura pelo nome ou pelo índice original (linha.iloc[4])
        # Usar o nome 'cast' é mais robusto caso a ordem mude
        elenco_raw = linha['cast']
        
        # Tratando valores nulos (NaN) que o Pandas gera quando a célula está vazia
        if pd.isna(elenco_raw):
            continue
            
        elenco_str = str(elenco_raw).strip()
        
        if elenco_str:
            # Separa os atores limpando os espaços
            atores = [ator.strip() for ator in elenco_str.split(',')]
            todos_os_elencos.append(atores)
                
    return todos_os_elencos