from collections import deque


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