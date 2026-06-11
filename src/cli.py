import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(
        description='Rede de Aeroportos do Brasil — Teoria dos Grafos'
    )
    parser.add_argument('--dataset', default='data/aeroportos_data.csv',
                        help='Caminho para aeroportos_data.csv')
    parser.add_argument('--adjacencias', default='data/adjacencias_aeroportos.csv',
                        help='Caminho para adjacencias_aeroportos.csv')
    parser.add_argument('--alg',
                        choices=['BFS', 'DFS', 'DIJKSTRA', 'BELLMAN_FORD', 'METRICAS', 'GERAR_ADJ', 'ARVORE_PERCURSO'], #Arvore como opção
                        default='METRICAS',
                        help='Algoritmo ou operação a executar')
    parser.add_argument('--source', help='Aeroporto de origem (código IATA)')
    parser.add_argument('--target', help='Aeroporto de destino (código IATA)')
    parser.add_argument('--out', default='out/', help='Pasta de saída')

    args = parser.parse_args()

    if args.alg == 'GERAR_ADJ':
        from solve import gerar_arquivo_adjacencias
        gerar_arquivo_adjacencias()

    elif args.alg == 'METRICAS':
        from solve import calcular_metricas_q3
        calcular_metricas_q3(args.dataset, args.adjacencias, args.out)

    elif args.alg == 'ARVORE_PERCURSO': #Adição ponto 7
        from solve import gerar_arvore_percurso_q7
        gerar_arvore_percurso_q7(args.dataset, args.adjacencias, args.out)

    elif args.alg == 'BFS':
        if not args.source:
            print('Erro: --source é obrigatório para BFS')
            sys.exit(1)
        from graphs.io import carregar_grafo
        from graphs.algorithms import bfs
        grafo, _ = carregar_grafo(args.dataset, args.adjacencias)
        ordem, niveis, predecessores = bfs(grafo, args.source)
        print(f'BFS a partir de {args.source}:')
        print(f'  Ordem de visita : {ordem}')
        print(f'  Níveis          : {niveis}')

    else:
        print(f'Algoritmo {args.alg} ainda não implementado nesta versão.')
        sys.exit(1)


if __name__ == '__main__':
    main()
