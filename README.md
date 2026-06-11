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
```

## 📂 Estrutura do Dataset (CSV)

```text
Coluna	Descrição	
iata	Código identificador único do aeroporto (3 letras)	
cidade	Nome da cidade onde o aeroporto está sediado	
regiao	Região do Brasil para fins de agrupamento e métricas	
```

# Dataset de Filmes (Parte 2)

```text
Coluna,Descrição
show_id,ID único para todo filme / programa de TV
type,Identifica se é um filme ou programa de TV
title,Título da obra
director,Diretor(es) do filme/programa
cast,Elenco/Atores envolvidos (base para o Grafo de Atores)
country,País onde o filme / programa de TV foi produzido
date_added,Data em que a obra foi adicionada na plataforma
realese_year,Ano de lançamento original do filme/série
rating,Classificação indicativa do filme/série na TV
duration,Duração total (em minutos para filmes ou número de temporadas para séries)
listed_in,Gênero / Categorias
description,Sinopse / Descrição resumida da obra
```
