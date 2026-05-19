import pandas as pd

from graphs.io import carregar_aeroportos
from graphs.graph import Grafo
from graphs.algorithms import calcular_graus, calcular_densidade_ego

def gerar_arquivo_adjacencias():
    """
    Cria o arquivo de conexões baseando-se em dados já validados na io.py.
    """
    df = carregar_aeroportos('data/aeroportos_data.csv')
    
    hubs = {
        'Sudeste': 'GRU', 
        'Nordeste': 'REC', 
        'Norte': 'MAO', 
        'Sul': 'POA', 
        'Centro-Oeste': 'BSB'
    }

    adjacencias = []

    # Conexões Regionais e com Hubs
    # Percorre os areoportos por região
    for regiao, grupo in df.groupby('regiao'):
        lista_aeroportos = grupo['iata'].tolist() # lista dos aeroportos da região atual percorrida
        
        # Verifica se o hub da região realmente está na região
        hub_da_regiao = hubs.get(regiao)
        if hub_da_regiao not in lista_aeroportos:
            print(f"Aviso: Hub {hub_da_regiao} não encontrado na região {regiao}!")

        # Modelação do Grafo Completo Regional: garante que todos se conectem com todos dentro da mesma região.
        for i in range(len(lista_aeroportos)):
            for j in range(i + 1, len(lista_aeroportos)):
                u, v = lista_aeroportos[i], lista_aeroportos[j]
                
                tipo = "regional"
                just = "Mesma região"
                peso = 1.0
                
                if u == hub_da_regiao or v == hub_da_regiao:
                    tipo = "regional_hub"
                    just = f"Conexão direta com hub {hub_da_regiao}"
                    peso = 1.5
                
                adjacencias.append([u, v, tipo, just, peso])

    # Conexões entre Hubs (Backbone Nacional)
    lista_hubs = list(hubs.values())
    for i in range(len(lista_hubs)):
        for j in range(i + 1, len(lista_hubs)):
            adjacencias.append([lista_hubs[i], lista_hubs[j], "hub_nacional", "Conexão entre hubs regionais", 2.0])

    # Salvar o resultado
    df_adj = pd.DataFrame(adjacencias, columns=['origem', 'destino', 'tipo_conexao', 'justificativa', 'peso'])
    df_adj.to_csv('data/adjacencias_aeroportos.csv', index=False)
    print("Sucesso: Arquivo 'adjacencias_aeroportos.csv' gerado com dados validados.")

def construir_grafo():
    df_nos = carregar_aeroportos('data/aeroportos_data.csv')
    df_adj = pd.read_csv('data/adjacencias_aeroportos.csv')

    g = Grafo()
    for _, row in df_nos.iterrows():
        g.adicionar_vertice(row['iata'], {'cidade': row['cidade'], 'regiao': row['regiao']})

    for _, row in df_adj.iterrows():
        g.adicionar_aresta(row['origem'], row['destino'], row['peso'])

    return g


def gerar_arquivo_graus(grafo):
    graus = calcular_graus(grafo)

    dados = sorted(
        [
            {
                'aeroporto': iata,
                'grau': grau,
                'densidade_ego': round(calcular_densidade_ego(grafo, iata), 4),
            }
            for iata, grau in graus.items()
        ],
        key=lambda x: -x['grau'],
    )

    pd.DataFrame(dados).to_csv('out/graus.csv', index=False)

    mais_conectado = max(graus, key=graus.get)
    maior_densidade = max(graus, key=lambda iata: calcular_densidade_ego(grafo, iata))

    print(f"Arquivo 'out/graus.csv' gerado com sucesso.")
    print(f"Aeroporto mais conectado:          {mais_conectado} (grau={graus[mais_conectado]})")
    print(f"Aeroporto com maior densidade local: {maior_densidade} "
          f"(densidade_ego={round(calcular_densidade_ego(grafo, maior_densidade), 4)})")


def main():
    try:
        # Passo 1: Gerar as conexões
        gerar_arquivo_adjacencias()

        # Passo 2: Construir o grafo
        g = construir_grafo()

        # Passo 3: Graus e rankings
        gerar_arquivo_graus(g)

    except Exception as e:
        print(f"Falha na execução: {e}")

if __name__ == "__main__":
    main()