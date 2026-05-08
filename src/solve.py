import pandas as pd

from graphs.io import carregar_aeroportos 
from graphs.graph import Grafo

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

def main():
    try:
        # Passo 1: Gerar as conexões
        gerar_arquivo_adjacencias()
        
        # Passo 2: Carregar o Grafo para a memória e seguir com o projeto...
        # g = Grafo()
        # ...
    except Exception as e:
        print(f"Falha na execução: {e}")

if __name__ == "__main__":
    main()