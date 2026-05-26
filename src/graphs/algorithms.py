import heapq
from collections import deque


def calcular_graus(grafo):
    return {no: len(vizinhos) for no, vizinhos in grafo.adj.items()}


def calcular_densidade_ego(grafo, no):
    vizinhos = set(grafo.adj[no].keys())
    ego_nos = vizinhos | {no}
    n = len(ego_nos)
    if n < 2:
        return 0.0
    max_arestas = n * (n - 1) / 2
    ego_list = list(ego_nos)
    arestas_reais = sum(
        1
        for i in range(len(ego_list))
        for j in range(i + 1, len(ego_list))
        if ego_list[j] in grafo.adj[ego_list[i]]
    )
    return arestas_reais / max_arestas


def bfs(grafo, aeroporto_inicial):

    if aeroporto_inicial not in grafo.adj:
        raise ValueError(f"O aeroporto {aeroporto_inicial} não existe no grafo.")

    fila = deque()
    visitados = set()
    ordem_visita = []
    niveis = {}
    predecessores = {}

    fila.append(aeroporto_inicial)
    visitados.add(aeroporto_inicial)
    niveis[aeroporto_inicial] = 0
    predecessores[aeroporto_inicial] = None

    while fila:
        aeroporto_atual = fila.popleft()
        ordem_visita.append(aeroporto_atual)

        for aeroporto_vizinho in grafo.adj[aeroporto_atual]:
            if aeroporto_vizinho not in visitados:
                visitados.add(aeroporto_vizinho)
                fila.append(aeroporto_vizinho)

                niveis[aeroporto_vizinho] = niveis[aeroporto_atual] + 1
                predecessores[aeroporto_vizinho] = aeroporto_atual

    return ordem_visita, niveis, predecessores

def dijkstra(grafo, origem, destino):
    fila = [(0.0, origem, [origem])]
    visitados = set()
    
    while fila:
        custo, no_atual, caminho = heapq.heappop(fila)
        
        if no_atual == destino:
            return custo, caminho
            
        if no_atual not in visitados:
            visitados.add(no_atual)
            
            for vizinho, peso in grafo.adj.get(no_atual, {}).items():
                if vizinho not in visitados:
                    heapq.heappush(fila, (custo + peso, vizinho, caminho + [vizinho]))
                    
    return float('inf'), []

def bfs_filmes(grafo, fonte_inicial):

    if hasattr(grafo, "adj"):
        adjacencias = grafo.adj
    else:
        adjacencias = grafo

    if fonte_inicial not in adjacencias:
        raise ValueError(f"A fonte {fonte_inicial} não existe no grafo de filmes.")

    fila = []
    inicio_fila = 0

    visitados = set()
    ordem_visita = []
    camadas = {}
    predecessores = {}
    ciclos = []

    arestas_de_ciclo_vistas = set()

    fila.append(fonte_inicial)
    visitados.add(fonte_inicial)
    camadas[fonte_inicial] = 0
    predecessores[fonte_inicial] = None

    while inicio_fila < len(fila):
        no_atual = fila[inicio_fila]
        inicio_fila += 1

        ordem_visita.append(no_atual)

        for vizinho in adjacencias[no_atual]:
            if vizinho not in visitados:
                visitados.add(vizinho)
                fila.append(vizinho)

                camadas[vizinho] = camadas[no_atual] + 1
                predecessores[vizinho] = no_atual

            else:
                if predecessores[no_atual] != vizinho and predecessores.get(vizinho) != no_atual:
                    chave_aresta = tuple(sorted([str(no_atual), str(vizinho)]))

                    if chave_aresta not in arestas_de_ciclo_vistas:
                        arestas_de_ciclo_vistas.add(chave_aresta)
                        ciclos.append((no_atual, vizinho))

    return ordem_visita, camadas, predecessores, ciclos