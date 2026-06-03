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

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from graphs.graph import Grafo
from graphs.algorithms import bfs, bfs_filmes
from graphs.io import carregar_e_validar_elencos
from solve import criar_grafo_atores

DATASET_PARTE2 = os.path.join(BASE_DIR, "data", "dataset_parte2.csv")


def montar_grafo_filmes_parte2():
    """
    Monta o grafo da Parte 2 usando as funções já existentes:
    - carregar_e_validar_elencos do io.py
    - criar_grafo_atores do solve.py
    """

    todos_os_elencos = carregar_e_validar_elencos(DATASET_PARTE2)
    grafo_atores = criar_grafo_atores(todos_os_elencos)

    return grafo_atores


def escolher_fontes_distintas(grafo, quantidade=3):
    """
    Escolhe fontes distintas para executar o BFS.
    Aqui usamos os atores com maior quantidade de conexões.
    """

    fontes = sorted(
        grafo.adj.keys(),
        key=lambda ator: len(grafo.adj[ator]),
        reverse=True
    )

    return fontes[:quantidade]


def imprimir_resultado_bfs(
    indice,
    fonte,
    ordem_visita,
    camadas,
    predecessores,
    ciclos,
    limite_exibicao=25
):
    print("\n" + "=" * 80)
    print(f"BFS {indice} - Fonte inicial: {fonte}")
    print("=" * 80)

    print(f"Total de vértices alcançados: {len(ordem_visita)}")
    print(f"Camada máxima encontrada: {max(camadas.values())}")
    print(f"Quantidade de ciclos encontrados: {len(ciclos)}")

    print("\nOrdem de visita BFS:")
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


def test_bfs_filmes_dataset_parte2_tres_fontes_terminal():
    """
    Executa BFS no grafo de filmes/atores da Parte 2
    a partir de 3 fontes distintas.
    """

    grafo_atores = montar_grafo_filmes_parte2()
    fontes = escolher_fontes_distintas(grafo_atores, quantidade=3)

    assert len(fontes) >= 3
    assert len(set(fontes)) == 3

    print("\n" + "#" * 80)
    print("[PARTE 2] BFS NO DATASET DE FILMES/ATORES")
    print("#" * 80)
    print(f"Fontes escolhidas: {fontes}")

    for indice, fonte in enumerate(fontes, start=1):
        ordem_visita, camadas, predecessores, ciclos = bfs_filmes(
            grafo_atores,
            fonte
        )

        imprimir_resultado_bfs(
            indice=indice,
            fonte=fonte,
            ordem_visita=ordem_visita,
            camadas=camadas,
            predecessores=predecessores,
            ciclos=ciclos
        )

        assert ordem_visita[0] == fonte
        assert camadas[fonte] == 0
        assert predecessores[fonte] is None
        assert len(ordem_visita) > 0
        assert isinstance(ciclos, list)