from src.graphs.algorithms import dfs_filmes


def test_dfs_filmes_tres_fontes_ordem_camadas_ciclos_classificacao():
    grafo_filmes = {
        "Filme A": ["Ator Ana", "Genero Drama"],
        "Ator Ana": ["Filme B"],
        "Filme B": ["Filme A"],
        "Genero Drama": ["Filme B"]
    }

    fontes = ["Filme A", "Ator Ana", "Genero Drama"]

    for fonte in fontes:
        ordem_visita, camadas, predecessores, ciclos, classificacao_arestas = dfs_filmes(
            grafo_filmes,
            fonte
        )

        assert ordem_visita[0] == fonte
        assert camadas[fonte] == 0
        assert predecessores[fonte] is None

        assert len(ordem_visita) > 0
        assert len(ciclos) > 0

        assert "arvore" in classificacao_arestas
        assert "retorno" in classificacao_arestas
        assert "avanco" in classificacao_arestas
        assert "cruzamento" in classificacao_arestas

        assert len(classificacao_arestas["arvore"]) > 0
        assert len(classificacao_arestas["retorno"]) > 0