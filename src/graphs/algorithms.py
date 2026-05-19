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