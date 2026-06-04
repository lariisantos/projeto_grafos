from __future__ import annotations

import csv
import json
import os
import sys
import numpy as np
from collections import deque

import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graphs.algorithms import dijkstra
from graphs.io import carregar_aeroportos, carregar_grafo, carregar_e_validar_elencos
from graphs.graph import Grafo
from graphs.metrics import metricas_subgrafo, ego_rede
from pyvis.network import Network
from viz import exportar_subgrafo_maior_grau
from viz import exportar_bfs_camadas

# Cria o arquivo adjacencias
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

# VISUALIZAÇÃO 5: Visualização de camadas via BFS  
def gerar_bfs_camadas(
    caminho_aeroportos: str = 'data/aeroportos_data.csv',
    caminho_adjacencias: str = 'data/adjacencias_aeroportos.csv',
    pasta_saida: str = 'out',
) -> str:
    
    return exportar_bfs_camadas(
        caminho_aeroportos=caminho_aeroportos,
        caminho_adjacencias=caminho_adjacencias,
        pasta_saida=pasta_saida,
    )

# Parte 2
def criar_grafo_atores(
    caminho_dataset: str = 'data/dataset_parte2.csv',
) -> Grafo:
    """
    [Parte 2] Carrega os dados de elencos utilizando a função importada, 
    monta e retorna o Grafo de Atores interconectados com base nas parcerias.
    """
    todos_os_elencos = carregar_e_validar_elencos(caminho_dataset)
    
    grafo = Grafo()
    encontros_atores = {}

    # 1. Cadastrar os vértices (Atores)
    for elenco in todos_os_elencos:
        for ator in elenco:
            grafo.adicionar_vertice(ator, {"tipo": "Ator"})

    # 2. Combinação manual dupla para calcular os pesos das parcerias
    for elenco in todos_os_elencos:
        n = len(elenco)
        if n > 1:
            for i in range(n):
                for j in range(i + 1, n):
                    ator1 = elenco[i]
                    ator2 = elenco[j]
                    
                    # Ordenação alfabética manual para consistência de chaves
                    if ator1 > ator2:
                        par = (ator2, ator1)
                    else:
                        par = (ator1, ator2)
                    
                    if par in encontros_atores:
                        encontros_atores[par] += 1
                    else:
                        encontros_atores[par] = 1

    # 3. Alimenta as arestas do objeto Grafo
    for (ator1, ator2), peso in encontros_atores.items():
        grafo.adicionar_aresta(ator1, ator2, peso)

    print(f"[Parte 2] Grafo de Atores criado com sucesso! Ordem={len(grafo.adj)} atores.")
    
    return grafo

def gerar_distribuicao_graus_parte2(grafo, pasta_saida: str = 'out') -> str:
    """Histograma da distribuição de graus do grafo de colaboração de atores Netflix."""
    os.makedirs(pasta_saida, exist_ok=True)

    graus = [len(vizinhos) for vizinhos in grafo.adj.values()]
    if not graus:
        print("[Parte 2] Grafo vazio, histograma não gerado.")
        return ""

    media = sum(graus) / len(graus)
    maximo = max(graus)
    bins = min(50, maximo + 1)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(graus, bins=bins, color='#2563eb', edgecolor='white', linewidth=0.4, alpha=0.87)
    ax.axvline(media, color='#ef4444', linestyle='--', linewidth=1.8, label=f'Média: {media:.1f}')
    ax.set_title(
        'Distribuição de Graus — Rede de Colaboração de Atores (Netflix)',
        fontsize=14, fontweight='bold', pad=15,
    )
    ax.set_xlabel('Grau (número de colaboradores únicos)', fontsize=12)
    ax.set_ylabel('Frequência (número de atores)', fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.legend(fontsize=10)

    stats = f'Atores: {len(graus):,}\nMáximo: {maximo}\nMédia: {media:.1f}'
    ax.text(0.97, 0.97, stats, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.85, edgecolor='#cbd5e1'))

    plt.tight_layout()
    caminho = os.path.join(pasta_saida, 'parte2_distribuicao_graus.png')
    plt.savefig(caminho, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[Parte 2] Distribuição de graus salva em: {caminho}")
    return caminho


def gerar_heatmap_distancias_parte2(grafo, pasta_saida: str = 'out', top_n: int = 12) -> str:
    """Heatmap das distâncias BFS (hops) entre os top-N atores mais conectados."""
    os.makedirs(pasta_saida, exist_ok=True)

    graus = {no: len(viz) for no, viz in grafo.adj.items()}
    if not graus:
        print("[Parte 2] Grafo vazio, heatmap não gerado.")
        return ""

    top_atores = sorted(graus, key=graus.get, reverse=True)[:top_n]

    def _bfs_dist(adj, origem):
        dist = {origem: 0}
        fila = deque([origem])
        while fila:
            no = fila.popleft()
            for viz in adj.get(no, {}):
                if viz not in dist:
                    dist[viz] = dist[no] + 1
                    fila.append(viz)
        return dist

    n = len(top_atores)
    matriz = np.full((n, n), np.nan)
    np.fill_diagonal(matriz, 0)

    for i, ator in enumerate(top_atores):
        dists = _bfs_dist(grafo.adj, ator)
        for j, outro in enumerate(top_atores):
            if i != j and outro in dists:
                matriz[i, j] = dists[outro]

    labels = [a[:18] for a in top_atores]

    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(matriz, cmap='YlOrRd_r', aspect='auto', vmin=0)

    cbar = plt.colorbar(im, ax=ax, shrink=0.82)
    cbar.set_label('Distância (hops BFS)', fontsize=11)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_title(
        f'Heatmap de Distâncias BFS — Top {top_n} Atores Mais Conectados\n'
        'Rede de Colaboração Netflix  (valor = hops mínimos entre atores)',
        fontsize=12, fontweight='bold', pad=15,
    )
    ax.set_xlabel('Ator (destino)', fontsize=11)
    ax.set_ylabel('Ator (origem)', fontsize=11)

    max_val = float(np.nanmax(matriz)) if not np.all(np.isnan(matriz)) else 1.0
    for i in range(n):
        for j in range(n):
            val = matriz[i, j]
            if not np.isnan(val):
                cor = 'white' if val < max_val * 0.4 else 'black'
                ax.text(j, i, str(int(val)), ha='center', va='center',
                        fontsize=9, fontweight='bold', color=cor)

    plt.tight_layout()
    caminho = os.path.join(pasta_saida, 'parte2_heatmap_distancias.png')
    plt.savefig(caminho, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[Parte 2] Heatmap de distâncias salvo em: {caminho}")
    return caminho


def gerar_ranking_atores_parte2(grafo, pasta_saida: str = 'out', top_n: int = 20) -> str:
    """Bar chart dos top-N atores mais conectados na rede Netflix."""
    os.makedirs(pasta_saida, exist_ok=True)

    graus = {no: len(viz) for no, viz in grafo.adj.items()}
    if not graus:
        print("[Parte 2] Grafo vazio, ranking não gerado.")
        return ""

    top = sorted(graus.items(), key=lambda kv: kv[1])[-top_n:]
    nomes = [kv[0][:28] for kv in top]
    valores = [kv[1] for kv in top]

    vmin, vmax = min(valores), max(valores)
    norm = [(v - vmin) / max(vmax - vmin, 1) for v in valores]
    cores = plt.cm.Blues([0.35 + 0.65 * n for n in norm])

    fig, ax = plt.subplots(figsize=(10, 8))
    bars = ax.barh(nomes, valores, color=cores, edgecolor='none')

    for bar, val in zip(bars, valores):
        ax.text(val + max(valores) * 0.005, bar.get_y() + bar.get_height() / 2,
                str(val), va='center', fontsize=9)

    ax.set_title(f'Top {top_n} Atores por Número de Colaboradores — Netflix',
                 fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel('Número de Colaboradores Únicos (Grau)', fontsize=11)
    ax.set_ylabel('Ator', fontsize=11)
    ax.grid(axis='x', linestyle='--', alpha=0.7)

    plt.tight_layout()
    caminho = os.path.join(pasta_saida, 'parte2_ranking_atores.png')
    plt.savefig(caminho, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[Parte 2] Ranking de atores salvo em: {caminho}")
    return caminho


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
        grafo_p2 = criar_grafo_atores()
        gerar_distribuicao_graus_parte2(grafo_p2)
        gerar_heatmap_distancias_parte2(grafo_p2)
        gerar_ranking_atores_parte2(grafo_p2)
    except Exception as e:
        print(f"Falha na execução: {e}")
        raise

if __name__ == "__main__":
    main()