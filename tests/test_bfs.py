from src.graphs.graph import Grafo
from src.graphs.algorithms import bfs


def test_bfs_niveis():

    grafo = Grafo()

    grafo.adicionar_vertice("REC", {"cidade": "Recife", "regiao": "Nordeste"})
    grafo.adicionar_vertice("SSA", {"cidade": "Salvador", "regiao": "Nordeste"})
    grafo.adicionar_vertice("GRU", {"cidade": "São Paulo", "regiao": "Sudeste"})
    grafo.adicionar_vertice("MAO", {"cidade": "Manaus", "regiao": "Norte"})

    grafo.adicionar_aresta("REC", "SSA", 1)
    grafo.adicionar_aresta("SSA", "GRU", 1)
    grafo.adicionar_aresta("REC", "MAO", 1)

    ordem_visita, niveis, predecessores = bfs(grafo, "REC")

    assert ordem_visita[0] == "REC"

    assert niveis["REC"] == 0
    assert niveis["SSA"] == 1
    assert niveis["MAO"] == 1
    assert niveis["GRU"] == 2

    assert predecessores["REC"] is None
    assert predecessores["SSA"] == "REC"
    assert predecessores["MAO"] == "REC"
    assert predecessores["GRU"] == "SSA"