import csv
import json
import os
import sys

import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graphs.algorithms import dijkstra
from graphs.io import carregar_aeroportos, carregar_grafo
from graphs.graph import Grafo
from graphs.metrics import metricas_subgrafo, ego_rede
from pyvis.network import Network
from viz import exportar_subgrafo_maior_grau

def gerar_arquivo_adjacencias():
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


def calcular_metricas(
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

def gerar_grafo_interativo():
    info_nos = {}
    try:
        with open('data/aeroportos_data.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                info_nos[row['iata']] = {'regiao': row['regiao']}
    except FileNotFoundError:
        pass

    try:
        with open('out/ego_aeroportos.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                aero = row['aeroporto']
                if aero not in info_nos:
                    info_nos[aero] = {}
                info_nos[aero]['grau'] = row['grau']
                info_nos[aero]['densidade_ego'] = row['densidade_ego']
    except FileNotFoundError:
        pass

    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black", select_menu=False, cdn_resources='remote')

    nos_adicionados = set()
    try:
        with open('data/adjacencias_aeroportos.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                u = row['origem']
                v = row['destino']
                peso = float(row['peso'])
                
                for no in (u, v):
                    if no not in nos_adicionados:
                        info = info_nos.get(no, {})
                        regiao = info.get('regiao', 'Desconhecida')
                        grau = info.get('grau', '?')
                        densidade = round(float(info.get('densidade_ego', 0.0)), 3) if info.get('densidade_ego') else '?'
                        
                        tooltip = f"Aeroporto: {no}\n Região: {regiao}\n Grau: {grau}\n Densidade Ego: {densidade}"
                        net.add_node(no, label=no, title=tooltip)
                        nos_adicionados.add(no)
                
                net.add_edge(u, v, value=peso)
    except FileNotFoundError:
        print("Erro: Arquivo adjacencias_aeroportos.csv não encontrado.")
        return

    os.makedirs('out', exist_ok=True)
    net.write_html('out/grafo_interativo.html')
    print("[Q9] grafo_interativo.html → Gerado com sucesso")

def gerar_arvore_percurso( 
    caminho_aeroportos: str = 'data/aeroportos_data.csv',
    caminho_adjacencias: str = 'data/adjacencias_aeroportos.csv',
    pasta_saida: str = 'out',
) -> str:
    from viz import exportar_arvore_percurso

    return exportar_arvore_percurso(
        caminho_aeroportos=caminho_aeroportos,
        caminho_adjacencias=caminho_adjacencias,
        pasta_saida=pasta_saida,
    )

#Explorações e visualizações analíticas
#Função auxiliar para carregar o arquivo ego_aeroportos.csv e validar sua existência.
def _carregar_dados_ego(pasta_dados: str) -> pd.DataFrame | None:
    
    caminho_csv = os.path.join(pasta_dados, 'ego_aeroportos.csv')
    if not os.path.exists(caminho_csv):
        print(f"Erro: {caminho_csv} não encontrado. Execute calcular_metricas primeiro.")
        return None
    
    try:
        return pd.read_csv(caminho_csv)
    except Exception as e:
        print(f"Erro ao ler os dados de ego-rede: {e}")
        return None
    
#VISUALIZAÇÃO 1: Distribuição de Graus (Histograma)
def gerar_histograma_graus(pasta_dados: str = 'out'):
    df_ego = _carregar_dados_ego(pasta_dados)
    if df_ego is None: return

    plt.figure(figsize=(8, 5))
    contagem_graus = df_ego['grau'].value_counts().sort_index()
    
    plt.bar(contagem_graus.index, 
            contagem_graus.values, 
            color='#4c72b0', 
            edgecolor='black', 
            alpha=0.9, 
            width=0.8)
    
    plt.title('Distribuição de Graus dos Aeroportos', fontsize=14, pad=15, fontweight='bold')
    plt.xlabel('Grau (Número de Interconexões)', fontsize=12)
    plt.ylabel('Frequência (Número de Aeroportos)', fontsize=12)
    
    plt.xticks(range(int(df_ego['grau'].min()), int(df_ego['grau'].max()) + 1))
    plt.grid(axis='y', linestyle='--', alpha=0.7) # Linhas de grade na horizontal
    
    plt.tight_layout()
    caminho_hist = os.path.join(pasta_dados, 'distribuicao_graus.png')
    plt.savefig(caminho_hist, dpi=300)
    plt.close()
    print(f"[AVD] Histograma salvo em: {caminho_hist}")

#VISUALIZAÇÃO 2: Ranking de Aeroportos Mais Conectados (Barra Ordenada)
def gerar_ranking_conectividade(pasta_dados: str = 'out'):
    caminho_csv = os.path.join(pasta_dados, 'ego_aeroportos.csv')
    
    if not os.path.exists(caminho_csv):
        print(f"Erro: {caminho_csv} não encontrado. Execute calcular_metricas primeiro.")
        return

    df_ego = pd.read_csv(caminho_csv)

    plt.figure(figsize=(10, 6))
    
    #Ordena os dados do menor para o maior (para que o maior fique no topo do gráfico horizontal)
    df_ranking = df_ego.sort_values(by='grau', ascending=True)
    
    #Criando um degradê de azul usando um colormap do Matplotlib
    valores_norm = (df_ranking['grau'] - df_ranking['grau'].min()) / (df_ranking['grau'].max() - df_ranking['grau'].min())
    cores_gradient = plt.cm.Blues(valores_norm * 0.6 + 0.4) 
    
    plt.barh(df_ranking['aeroporto'], df_ranking['grau'], color=cores_gradient, edgecolor='none')
    
    plt.title('Ranking de Aeroportos por Nível de Conectividade', fontsize=14, pad=15, fontweight='bold')
    plt.xlabel('Grau (Número de Interconexões)', fontsize=12)
    plt.ylabel('Aeroporto (IATA)', fontsize=12)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    caminho_barra = os.path.join(pasta_dados, 'ranking_aeroportos.png')
    plt.savefig(caminho_barra, dpi=300)
    plt.close()
    print(f"[AVD] Gráfico de barras salvo em: {caminho_barra}")

#Função auxiliar para carregar as regioes
def _carregar_dados_regioes(pasta_dados: str) -> list | None:
    caminho_json = os.path.join(pasta_dados, 'regioes.json')
    if not os.path.exists(caminho_json):
        print(f"Erro: {caminho_json} não encontrado. Execute calcular_metricas primeiro.")
        return None

    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler os dados das regiões: {e}")
        return None

#VISUALIZAÇÃO 3: Comparação entre Regiões
def gerar_comparacao_regioes(pasta_dados: str = 'out'):
    dados = _carregar_dados_regioes(pasta_dados)
    if not dados: return

    regioes = [d['regiao'] for d in dados]
    ordens = [d['ordem'] for d in dados]
    tamanhos = [d['tamanho'] for d in dados]
    densidades = [d['densidade'] for d in dados]

    cores = ['#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3']
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Comparação entre Regiões', fontsize=14, fontweight='bold')

    for ax, valores, titulo, ylabel in zip(
        axes,
        [ordens, tamanhos, densidades],
        ['Ordem (Nós)', 'Tamanho (Arestas)', 'Densidade'],
        ['Quantidade', 'Quantidade', 'Valor'],
    ):
        ax.bar(regioes, valores, color=cores[:len(regioes)], edgecolor='black', alpha=0.9)
        ax.set_title(titulo, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.tick_params(axis='x', rotation=20)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    caminho = os.path.join(pasta_dados, 'comparacao_regioes.png')
    plt.savefig(caminho, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[AVD] Comparação entre regiões salva em: {caminho}")

#VISUALIZAÇÃO 4: Subgrafo dos aeroportos com maior grau 
def gerar_subgrafo_maior_grau(
    caminho_aeroportos: str = 'data/aeroportos_data.csv',
    caminho_adjacencias: str = 'data/adjacencias_aeroportos.csv',
    pasta_saida: str = 'out',
) -> str:
    
    return exportar_subgrafo_maior_grau(
        caminho_aeroportos=caminho_aeroportos,
        caminho_adjacencias=caminho_adjacencias,
        pasta_saida=pasta_saida,
    )


def gerar_bfs_camadas(
    caminho_aeroportos: str = 'data/aeroportos_data.csv',
    caminho_adjacencias: str = 'data/adjacencias_aeroportos.csv',
    pasta_saida: str = 'out',
) -> str:
    from viz import exportar_bfs_camadas
    return exportar_bfs_camadas(
        caminho_aeroportos=caminho_aeroportos,
        caminho_adjacencias=caminho_adjacencias,
        pasta_saida=pasta_saida,
    )


calcular_metricas_q3 = calcular_metricas
gerar_arvore_percurso_q7 = gerar_arvore_percurso


def main():
    try:
        gerar_arquivo_adjacencias()
        calcular_metricas()
        gerar_arvore_percurso()
        gerar_grafo_interativo()
        gerar_histograma_graus()
        gerar_ranking_conectividade()
        gerar_comparacao_regioes()
        gerar_subgrafo_maior_grau()
        gerar_bfs_camadas()
    except Exception as e:
        print(f"Falha na execução: {e}")
        raise


if __name__ == "__main__":
    main()