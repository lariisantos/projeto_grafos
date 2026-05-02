# Projeto Final: Rede de Aeroportos do Brasil (Parte 1)

Este projeto consiste na modelagem e análise da malha aérea brasileira utilizando a Teoria dos Grafos. 

O objetivo é aplicar algoritmos de busca e caminhos mínimos para entender a conectividade entre diferentes regiões do Brasil.

## 📂 Estrutura de Pastas (Obrigatória)

A organização do projeto segue rigorosamente a estrutura definida nos requisitos:

```text
projeto-grafos/
├── README.md                 # Instruções e documentação
├── requirements.txt          # Dependências do projeto (pandas, etc.)
├── data/
│   ├── aeroportos_data.csv   # Dados fornecidos (IATA, Cidade, Região)
│   ├── adjacencias_aeroportos.csv # Arestas construídas pelo grupo
│   └── rotas.csv             # Pares para teste de caminhos mínimos
├── out/                      # Resultados das análises (JSON, CSV, Imagens)
├── src/
│   ├── cli.py                # Interface de linha de comando
│   ├── solve.py              # Script principal de execução
│   ├── graphs/
│   │   ├── io.py             # Carregamento e normalização de dados
│   │   └── graph.py          # Implementação da Lista de Adjacência
│   ├── algorithms.py         # Implementação de BFS, DFS e Dijkstra
│   └── viz.py                # Visualizações analíticas e interativas
└── tests/                    # Testes unitários obrigatórios