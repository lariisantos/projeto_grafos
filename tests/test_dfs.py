import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from graphs.algorithms import dfs_filmes
from solve import criar_grafo_atores

DATASET_PARTE2 = os.path.join(BASE_DIR, "data", "dataset_parte2.csv")


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

def escolher_fontes_distintas(grafo, quantidade=3):
    """
    Escolhe fontes distintas para executar o DFS.
    Aqui usamos os atores com maior quantidade de conexões.
    """

    fontes = sorted(
        grafo.adj.keys(),
        key=lambda ator: len(grafo.adj[ator]),
        reverse=True
    )

    return fontes[:quantidade]


def imprimir_resultado_dfs(
    indice,
    fonte,
    ordem_visita,
    camadas,
    predecessores,
    ciclos,
    classificacao_arestas,
    limite_exibicao=25
):
    print("\n" + "=" * 80)
    print(f"DFS {indice} - Fonte inicial: {fonte}")
    print("=" * 80)

    print(f"Total de vértices alcançados: {len(ordem_visita)}")
    print(f"Profundidade máxima encontrada: {max(camadas.values())}")
    print(f"Quantidade de ciclos encontrados: {len(ciclos)}")

    print("\nOrdem de visita DFS:")
    for posicao, no in enumerate(ordem_visita[:limite_exibicao], start=1):
        print(
            f"{posicao:02d}. {no} "
            f"| camada={camadas[no]} "
            f"| predecessor={predecessores.get(no)}"
        )

    if len(ordem_visita) > limite_exibicao:
        print(
            f"... exibindo apenas os primeiros {limite_exibicao} "
            f"de {len(ordem_visita)} vértices visitados."
        )

    print("\nResumo das camadas:")
    resumo_camadas = {}

    for no, camada in camadas.items():
        resumo_camadas[camada] = resumo_camadas.get(camada, 0) + 1

    for camada in sorted(resumo_camadas.keys())[:10]:
        print(f"Camada {camada}: {resumo_camadas[camada]} vértice(s)")

    print("\nExemplos de ciclos encontrados:")
    if ciclos:
        for ciclo in ciclos[:10]:
            print(f"{ciclo[0]} -> {ciclo[1]}")
    else:
        print("Nenhum ciclo encontrado.")

    print("\nClassificação das arestas:")
    for tipo, arestas in classificacao_arestas.items():
        print(f"{tipo}: {len(arestas)} aresta(s)")


def test_dfs_filmes_dataset_parte2_tres_fontes_terminal():
    """
    Executa DFS no grafo de filmes/atores da Parte 2
    a partir de 3 fontes distintas.
    """

    sys.setrecursionlimit(200000)

    grafo_atores = criar_grafo_atores()
    fontes = escolher_fontes_distintas(grafo_atores, quantidade=3)

    assert len(fontes) >= 3
    assert len(set(fontes)) == 3

    print("\n" + "#" * 80)
    print("[PARTE 2] DFS NO DATASET DE FILMES/ATORES")
    print("#" * 80)
    print(f"Fontes escolhidas: {fontes}")

    for indice, fonte in enumerate(fontes, start=1):
        ordem_visita, camadas, predecessores, ciclos, classificacao_arestas = dfs_filmes(
            grafo_atores,
            fonte
        )

        imprimir_resultado_dfs(
            indice=indice,
            fonte=fonte,
            ordem_visita=ordem_visita,
            camadas=camadas,
            predecessores=predecessores,
            ciclos=ciclos,
            classificacao_arestas=classificacao_arestas
        )

        assert ordem_visita[0] == fonte
        assert camadas[fonte] == 0
        assert predecessores[fonte] is None
        assert len(ordem_visita) > 0
        assert isinstance(ciclos, list)

        assert "arvore" in classificacao_arestas
        assert "retorno" in classificacao_arestas
        assert "avanco" in classificacao_arestas
        assert "cruzamento" in classificacao_arestas