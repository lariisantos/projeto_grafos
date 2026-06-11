from __future__ import annotations

import csv
import json
import os
import sys
import time
import random
import heapq
import numpy as np
from collections import deque

import pandas as pd
import matplotlib.pyplot as plt  # usado pelas visualizações da Parte 2 (abaixo)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graphs.algorithms import dijkstra
from graphs.io import carregar_aeroportos, carregar_grafo, carregar_e_validar_elencos
from graphs.graph import Grafo
from graphs.metrics import metricas_subgrafo, ego_rede
from export_react import (
    exportar_react_data, exportar_react_data_parte2,
    exportar_grafo_render_json, buildar_react,
)

# Toda a camada visual do projeto vive em viz.py (módulo visual único).
# solve.py apenas calcula dados e orquestra a geração das visualizações.
from viz import (
    exportar_arvore_percurso,
    exportar_grafo_interativo,
    exportar_subgrafo_maior_grau,
    exportar_bfs_camadas,
    exportar_histograma_graus,
    exportar_ranking_conectividade,
    exportar_comparacao_regioes,
    exportar_avd_visualizacoes,
)


# ══════════════════════════════════════════════════════════════════════════
# DADOS — modelagem e métricas do grafo (Parte 1)
# ══════════════════════════════════════════════════════════════════════════

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


def calcular_rotas_dijkstra():
    grafo, _ = carregar_grafo('data/aeroportos_data.csv', 'data/adjacencias_aeroportos.csv')
    rotas = []

    try:
        with open('data/rotas.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('origem') and row.get('destino'):
                    rotas.append((row['origem'].strip(), row['destino'].strip()))
    except FileNotFoundError:
        pass

    resultados = []
    for orig, dest in rotas:
        if orig not in grafo.adj or dest not in grafo.adj:
            resultados.append([orig, dest, float('inf'), "Sem caminho viável"])
            print(f"[Q6]   {orig} -> {dest:3s} -> Erro: Aeroporto não encontrado no grafo.")
            continue

        custo, caminho = dijkstra(grafo, orig, dest)
        str_caminho = " -> ".join(caminho) if caminho else "Sem caminho viável"

        resultados.append([orig, dest, custo, str_caminho])
        print(f"[Q6]   {orig} -> {dest:3s} -> custo={custo:.1f}, caminho=[{str_caminho}]")

    os.makedirs('out', exist_ok=True)
    with open('out/distancias_rotas.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['origem', 'destino', 'custo', 'caminho'])
        for res in resultados:
            writer.writerow(res)

    print(f"[Q6] distancias_rotas.csv -> {len(resultados)} rotas processadas")


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
    print(f"[Q3] global.json  -> ordem={m_global['ordem']}, tamanho={m_global['tamanho']}, densidade={m_global['densidade']:.4f}")

    mapa_regioes: dict[str, set] = {}
    for _, row in df.iterrows():
        mapa_regioes.setdefault(row['regiao'], set()).add(row['iata'])

    lista_regioes = []
    for regiao in sorted(mapa_regioes.keys()):
        nos_regiao = mapa_regioes[regiao]
        m = metricas_subgrafo(grafo, nos_regiao)
        lista_regioes.append({'regiao': regiao, **m})
        print(f"[Q3]   {regiao:15s} -> ordem={m['ordem']}, tamanho={m['tamanho']}, densidade={m['densidade']:.4f}")

    with open(os.path.join(pasta_saida, 'regioes.json'), 'w', encoding='utf-8') as f:
        json.dump(lista_regioes, f, ensure_ascii=False, indent=2)
    print(f"[Q3] regioes.json -> {len(lista_regioes)} regiões")

    rows_ego = [ego_rede(grafo, no) for no in sorted(grafo.adj.keys())]
    df_ego = pd.DataFrame(rows_ego, columns=['aeroporto', 'grau', 'ordem_ego', 'tamanho_ego', 'densidade_ego'])
    df_ego.to_csv(os.path.join(pasta_saida, 'ego_aeroportos.csv'), index=False)
    print(f"[Q3] ego_aeroportos.csv -> {len(rows_ego)} aeroportos")

    return m_global, lista_regioes, rows_ego


# ══════════════════════════════════════════════════════════════════════════
# VISUALIZAÇÕES — wrappers finos que delegam ao módulo visual (viz.py)
# ══════════════════════════════════════════════════════════════════════════

def gerar_arvore_percurso(  # Q7
    caminho_aeroportos: str = 'data/aeroportos_data.csv',
    caminho_adjacencias: str = 'data/adjacencias_aeroportos.csv',
    pasta_saida: str = 'out',
) -> str:
    return exportar_arvore_percurso(
        caminho_aeroportos=caminho_aeroportos,
        caminho_adjacencias=caminho_adjacencias,
        pasta_saida=pasta_saida,
    )


def gerar_grafo_interativo() -> str:  # Q9
    return exportar_grafo_interativo()


def gerar_subgrafo_maior_grau(  # Q8
    caminho_aeroportos: str = 'data/aeroportos_data.csv',
    caminho_adjacencias: str = 'data/adjacencias_aeroportos.csv',
    pasta_saida: str = 'out',
) -> str:
    return exportar_subgrafo_maior_grau(
        caminho_aeroportos=caminho_aeroportos,
        caminho_adjacencias=caminho_adjacencias,
        pasta_saida=pasta_saida,
    )


def gerar_bfs_camadas(  # Q8
    caminho_aeroportos: str = 'data/aeroportos_data.csv',
    caminho_adjacencias: str = 'data/adjacencias_aeroportos.csv',
    pasta_saida: str = 'out',
) -> str:
    return exportar_bfs_camadas(
        caminho_aeroportos=caminho_aeroportos,
        caminho_adjacencias=caminho_adjacencias,
        pasta_saida=pasta_saida,
    )


def gerar_histograma_graus(pasta_dados: str = 'out'):       # Q8
    return exportar_histograma_graus(pasta_dados)


def gerar_ranking_conectividade(pasta_dados: str = 'out'):  # Q8
    return exportar_ranking_conectividade(pasta_dados)


def gerar_comparacao_regioes(pasta_dados: str = 'out'):     # Q8
    return exportar_comparacao_regioes(pasta_dados)


# ──────────────────────────────────────────────────────────────
# Q10 — Análise exploratória e explanatória (AVD)
# Relatório textual (dados) aqui; as 4 visualizações ficam em viz.py.
# ──────────────────────────────────────────────────────────────
def _relatorio_avd(df_ego, glob, regioes):
    sep = "=" * 58
    print(f"\n[Q10] {sep}")
    print("[Q10]  ANALISE EXPLORATORIA E EXPLANATORIA -- Q10")
    print(f"[Q10] {sep}")
    print(f"[Q10] Ordem={glob['ordem']}, Tamanho={glob['tamanho']}, Densidade={glob['densidade']:.4f}")
    print(f"[Q10] Grau medio={df_ego['grau'].mean():.2f}, max={df_ego['grau'].max()}, min={df_ego['grau'].min()}")
    media = df_ego["grau"].mean()
    std = df_ego["grau"].std()
    hubs = df_ego[df_ego["grau"] >= media + std].sort_values("grau", ascending=False)
    print(f"[Q10] Hubs (grau >= {media + std:.1f}):")
    for _, h in hubs.iterrows():
        print(f"  {h['aeroporto']} ({h['regiao']}) grau={h['grau']}")
    print(f"[Q10] {sep}\n")


def analise_avd(pasta_saida: str = 'out', pasta_data: str = 'data'):
    """Q10 — imprime o relatório textual e gera as 4 visualizações (via viz.py)."""
    df_ego = pd.read_csv(os.path.join(pasta_saida, 'ego_aeroportos.csv'))
    df_aero = pd.read_csv(os.path.join(pasta_data, 'aeroportos_data.csv'))
    df_ego = (
        df_ego.merge(df_aero[['iata', 'regiao']], left_on='aeroporto', right_on='iata', how='left')
        .drop(columns='iata')
    )
    with open(os.path.join(pasta_saida, 'global.json'), encoding='utf-8') as f:
        glob = json.load(f)
    with open(os.path.join(pasta_saida, 'regioes.json'), encoding='utf-8') as f:
        regioes = json.load(f)

    _relatorio_avd(df_ego, glob, regioes)
    exportar_avd_visualizacoes(pasta_saida, pasta_data)


# ══════════════════════════════════════════════════════════════════════════
# PARTE 2 — Dataset maior (em desenvolvimento pelos colegas)
# ══════════════════════════════════════════════════════════════════════════
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


def subgrafo_top_grau(grafo: Grafo, n_atores: int = 15000) -> Grafo:
    """
    [Parte 2] Subgrafo INDUZIDO com os `n_atores` vértices de maior grau e
    apenas as arestas entre eles. Preserva o núcleo mais conectado da rede.
    """
    graus = {no: len(viz) for no, viz in grafo.adj.items()}
    selecionados = sorted(graus, key=graus.get, reverse=True)[:n_atores]
    sel_set = set(selecionados)

    sub = Grafo()
    for ator in selecionados:
        sub.adicionar_vertice(ator, grafo.nodes_info.get(ator, {"tipo": "Ator"}))
    for ator in selecionados:
        for viz, peso in grafo.adj[ator].items():
            if viz in sel_set:
                sub.adicionar_aresta(ator, viz, peso)

    arestas = sum(len(v) for v in sub.adj.values()) // 2
    print(f"[Parte 2] Subgrafo top-{n_atores} por grau criado. "
          f"Ordem={len(sub.adj)} atores, arestas={arestas}.")
    return sub


def gerar_grafo_15k_render(grafo_completo: Grafo, n_atores: int = 15000) -> Grafo:
    """
    [Parte 2] Versão do grafo de colaboração com os `n_atores` atores mais
    conectados, com layout 2D calculado e exportado para o Canvas do front
    (dashboard/public/grafo_parte2_15k.json) desenhar TODOS os nós.
    """
    sub = subgrafo_top_grau(grafo_completo, n_atores)
    exportar_grafo_render_json(sub, nome_arquivo=f"grafo_parte2_{n_atores // 1000}k.json")
    return sub


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
    ax.set_xlim(0, 125)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.legend(fontsize=10)

    fora_janela = sum(1 for g in graus if g > 125)
    stats = f'Atores: {len(graus):,}\nMáximo: {maximo}\nMédia: {media:.1f}\n(+{fora_janela} acima de 125)'
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
        f'Quantos atores separam dois hubs da Netflix?\n'
        f'Distâncias BFS entre os {top_n} atores mais conectados  (0 = mesmo ator)',
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

def executar_benchmarks(grafo_15k, caminho_saida="out/parte2_report.json"):
    """
    Executa a análise de tempo para BFS, DFS, Dijkstra e Bellman-Ford
    no subgrafo de 15k atores e exporta o relatório em JSON.
    """
    # Garante que a pasta de saída existe
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    
    # Seleciona um nó de origem aleatório (ou fixo) para consistência dos testes
    atores_disponiveis = list(grafo_15k.adj.keys())
    if not atores_disponiveis:
        print("Erro: Grafo vazio.")
        return
    
    # Pegamos um nó de alto grau para garantir que a busca explore bastante
    origem = atores_disponiveis[0] 
    
    # Dicionário para armazenar as métricas
    report = {
        "configuracao": {
            "num_vertices": len(grafo_15k.adj),
            "no_origem_teste": origem
        },
        "metricas_tempo_segundos": {}
    }

    # ==========================================
    # 1. TESTE: BFS (Busca em Largura)
    # ==========================================
    inicio = time.perf_counter()
    # Mock/Chamada da sua BFS real:
    # _ = sua_bfs(grafo_15k, origem)
    visitados_bfs = set([origem])
    fila = deque([origem])
    while fila:
        u = fila.popleft()
        for v in grafo_15k.adj[u]:
            if v not in visitados_bfs:
                visitados_bfs.add(v)
                fila.append(v)
    fim = time.perf_counter()
    report["metricas_tempo_segundos"]["BFS"] = fim - inicio

    # ==========================================
    # 2. TESTE: DFS (Busca em Profundidade - Iterativa para evitar estouro de pilha)
    # ==========================================
    inicio = time.perf_counter()
    visitados_dfs = set()
    pilha = [origem]
    while pilha:
        u = pilha.pop()
        if u not in visitados_dfs:
            visitados_dfs.add(u)
            for v in grafo_15k.adj[u]:
                if v not in visitados_dfs:
                    pilha.append(v)
    fim = time.perf_counter()
    report["metricas_tempo_segundos"]["DFS"] = fim - inicio

    # ==========================================
    # 3. TESTE: Dijkstra (Com Min-Heap / heapq)
    # ==========================================
    inicio = time.perf_counter()
    distancias = {no: float('inf') for no in grafo_15k.adj}
    distancias[origem] = 0
    prio_queue = [(0, origem)]
    
    while prio_queue:
        dist_u, u = heapq.heappop(prio_queue)
        if dist_u > distancias[u]:
            continue
        for v, peso in grafo_15k.adj[u].items():
            # Considerando o peso como inverso do número de encontros (ou o próprio peso)
            custo = 1 / peso if peso > 0 else 1 
            if distancias[u] + custo < distancias[v]:
                distancias[v] = distancias[u] + custo
                heapq.heappush(prio_queue, (distancias[v], v))
    fim = time.perf_counter()
    report["metricas_tempo_segundos"]["Dijkstra"] = fim - inicio

    # ==========================================
    # 4. TESTE: Bellman-Ford (Aviso: O(V * E) em 15k nós pode demorar minutos)
    # ==========================================
    # Para não travar sua entrega, faremos uma versão otimizada com early-stop
    inicio = time.perf_counter()
    dist_bf = {no: float('inf') for no in grafo_15k.adj}
    dist_bf[origem] = 0
    
    # Lista de todas as arestas para iteração rápida
    arestas = []
    for u in grafo_15k.adj:
        for v, peso in grafo_15k.adj[u].items():
            arestas.append((u, v, 1/peso if peso > 0 else 1))
            
    # Relaxamento V-1 vezes
    for _ in range(len(grafo_15k.adj) - 1):
        mudou = False
        for u, v, peso in arestas:
            if dist_bf[u] != float('inf') and dist_bf[u] + peso < dist_bf[v]:
                dist_bf[v] = dist_bf[u] + peso
                mudou = True
        if not mudou: # Otimização: se não houve alteração, converge precoce
            break
            
    fim = time.perf_counter()
    report["metricas_tempo_segundos"]["Bellman-Ford"] = fim - inicio

    # ==========================================
    # EXPORTAÇÃO PARA JSON
    # ==========================================
    with open(caminho_saida, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
        
    print(f"\n[OK] Relatório de performance salvo com sucesso em: {caminho_saida}")

def main():
    try:
        # ── Dados (Parte 1) ──
        gerar_arquivo_adjacencias()      # arestas do grafo
        calcular_metricas()              # Q3 — global/regioes/ego
        calcular_rotas_dijkstra()        # Q6 — distancias_rotas.csv

        # ── Visualizações estáticas Parte 1 em out/ (módulo viz.py) ──
        gerar_arvore_percurso()          # Q7
        gerar_grafo_interativo()         # Q9
        gerar_histograma_graus()         # Q8
        gerar_ranking_conectividade()    # Q8
        gerar_comparacao_regioes()       # Q8
        gerar_subgrafo_maior_grau()      # Q8
        gerar_bfs_camadas()              # Q8
        analise_avd()                    # Q10 — relatório + 4 visualizações

        # ── Parte 2 — grafo de atores + visualizações (colegas) ──
        grafo_p2 = criar_grafo_atores()
        gerar_distribuicao_graus_parte2(grafo_p2)
        gerar_heatmap_distancias_parte2(grafo_p2)
        gerar_ranking_atores_parte2(grafo_p2)
        gerar_grafo_15k_render(grafo_p2)  # layout 15k p/ Canvas -> public/grafo_parte2_15k.json

        # ── Front React (camada de apresentação por cima dos dados) ──
        exportar_react_data()            # Parte 1 -> dashboard/src/data.js
        exportar_react_data_parte2(grafo_p2)  # Parte 2 -> dashboard/src/data_parte2.js
        buildar_react()                  # build do app React
        executar_benchmarks(grafo_p2)  # Q10 — benchmarks de algoritmos no grafo de atores (JSON em out/parte2_report.json)
    except Exception as e:
        print(f"Falha na execução: {e}")
        raise


if __name__ == "__main__":
    main()
