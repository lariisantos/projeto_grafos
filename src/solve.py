import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graphs.io import carregar_aeroportos, carregar_grafo
from graphs.graph import Grafo
from graphs.metrics import metricas_subgrafo, ego_rede

from graphs.algorithms import calcular_graus, calcular_densidade_ego

def gerar_arquivo_adjacencias():
    """Cria o arquivo de conexões baseando-se em dados já validados na io.py."""
    df = carregar_aeroportos('data/aeroportos_data.csv')

    hubs = {
        'Sudeste': 'GRU',
        'Nordeste': 'REC',
        'Norte': 'MAO',
        'Sul': 'POA',
        'Centro-Oeste': 'BSB',
    }

    adjacencias = []

    for regiao, grupo in df.groupby('regiao'):
        lista_aeroportos = grupo['iata'].tolist()

        hub_da_regiao = hubs.get(regiao)
        if hub_da_regiao not in lista_aeroportos:
            print(f"Aviso: Hub {hub_da_regiao} não encontrado na região {regiao}!")

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

    lista_hubs = list(hubs.values())
    for i in range(len(lista_hubs)):
        for j in range(i + 1, len(lista_hubs)):
            adjacencias.append([lista_hubs[i], lista_hubs[j], "hub_nacional", "Conexão entre hubs regionais", 2.0])

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



def calcular_metricas_q3(
    caminho_aeroportos: str = 'data/aeroportos_data.csv',
    caminho_adjacencias: str = 'data/adjacencias_aeroportos.csv',
    pasta_saida: str = 'out',
) -> tuple:
    os.makedirs(pasta_saida, exist_ok=True)

    grafo, df = carregar_grafo(caminho_aeroportos, caminho_adjacencias)

    todos_nos = set(grafo.adj.keys())
    m_global = metricas_subgrafo(grafo, todos_nos)
    with open(os.path.join(pasta_saida, 'global.json'), 'w', encoding='utf-8') as f:
        json.dump(m_global, f, ensure_ascii=False, indent=2)
    print(f"[Q3] global.json  → ordem={m_global['ordem']}, tamanho={m_global['tamanho']}, densidade={m_global['densidade']:.4f}")

    mapa_regioes: dict[str, set] = {}
    for _, row in df.iterrows():
        mapa_regioes.setdefault(row['regiao'], set()).add(row['iata'])

    lista_regioes = []
    for regiao in sorted(mapa_regioes.keys()):
        nos_regiao = mapa_regioes[regiao]
        m = metricas_subgrafo(grafo, nos_regiao)
        lista_regioes.append({'regiao': regiao, **m})
        print(f"[Q3]   {regiao:15s} → ordem={m['ordem']}, tamanho={m['tamanho']}, densidade={m['densidade']:.4f}")

    with open(os.path.join(pasta_saida, 'regioes.json'), 'w', encoding='utf-8') as f:
        json.dump(lista_regioes, f, ensure_ascii=False, indent=2)
    print(f"[Q3] regioes.json → {len(lista_regioes)} regiões")

    rows_ego = [ego_rede(grafo, no) for no in sorted(grafo.adj.keys())]
    df_ego = pd.DataFrame(rows_ego, columns=['aeroporto', 'grau', 'ordem_ego', 'tamanho_ego', 'densidade_ego'])
    df_ego.to_csv(os.path.join(pasta_saida, 'ego_aeroportos.csv'), index=False)
    print(f"[Q3] ego_aeroportos.csv → {len(rows_ego)} aeroportos")

    return m_global, lista_regioes, rows_ego

def main():
    try:
        gerar_arquivo_adjacencias()

        # Passo 2: Construir o grafo
        g = construir_grafo()

        # Passo 3: Graus e rankings
        gerar_arquivo_graus(g)

        calcular_metricas_q3()
    except Exception as e:
        print(f"Falha na execução: {e}")
        raise


if __name__ == "__main__":
    main()
