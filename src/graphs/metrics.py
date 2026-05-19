def calcular_densidade(ordem: int, tamanho: int) -> float:
    if ordem < 2:
        return 0.0
    return 2 * tamanho / (ordem * (ordem - 1))


def metricas_subgrafo(grafo, nos: set) -> dict:
    ordem = len(nos)
    tamanho = 0
    for u in nos:
        for v in grafo.adj.get(u, {}):
            if v in nos and u < v:
                tamanho += 1
    densidade = calcular_densidade(ordem, tamanho)
    return {
        "ordem": ordem,
        "tamanho": tamanho,
        "densidade": round(densidade, 6),
    }


def ego_rede(grafo, no: str) -> dict:
    vizinhos = set(grafo.adj.get(no, {}).keys())
    grau = len(vizinhos)
    ego_nos = {no} | vizinhos

    tamanho = 0
    lista = list(ego_nos)
    for i in range(len(lista)):
        for j in range(i + 1, len(lista)):
            u, v = lista[i], lista[j]
            if v in grafo.adj.get(u, {}):
                tamanho += 1

    ordem = len(ego_nos)
    return {
        "aeroporto": no,
        "grau": grau,
        "ordem_ego": ordem,
        "tamanho_ego": tamanho,
        "densidade_ego": round(calcular_densidade(ordem, tamanho), 6),
    }
