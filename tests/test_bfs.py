from src.graphs.graph import Grafo
from src.graphs.algorithms import bfs, bfs_filmes


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

def test_bfs_filmes():
    grafo_filmes = {
        "Filme A": ["Ator Ana", "Drama"],
        "Ator Ana": ["Filme A", "Filme B"],
        "Drama": ["Filme A", "Filme B", "Filme C"],
        "Filme B": ["Ator Ana", "Drama"],
        "Filme C": ["Drama"],
    }

    fontes = ["Filme A", "Ator Ana", "Filme C"]

    for fonte in fontes:
        ordem_visita, camadas, predecessores, ciclos = bfs_filmes(grafo_filmes, fonte)

        assert ordem_visita[0] == fonte
        assert camadas[fonte] == 0
        assert predecessores[fonte] is None

        assert len(ordem_visita) == len(grafo_filmes)

        for no in grafo_filmes:
            assert no in camadas

        assert len(ciclos) > 0