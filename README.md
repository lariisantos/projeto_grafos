# Projeto Final: Análise de Redes com Grafos

Modelagem e análise de dois grafos distintos usando Teoria dos Grafos:

- **Parte 1** — Malha aérea brasileira: 20 aeroportos e 45 rotas, com algoritmos de busca, caminhos mínimos e análise exploratória.
- **Parte 2** — Rede de colaboração de atores Netflix: ~36 mil atores conectados por filmes/séries em comum, com benchmarks de desempenho.

Os resultados são exibidos em um **dashboard React interativo**, gerado automaticamente pelo pipeline Python.

---

## Estrutura de Pastas

```text
projeto_grafos/
├── README.md
├── requirements.txt
├── data/
│   ├── aeroportos_data.csv          # IATA, cidade, região (Parte 1)
│   ├── adjacencias_aeroportos.csv   # Arestas com tipo de conexão (Parte 1)
│   ├── rotas.csv                    # Pares origem-destino para caminhos mínimos
│   └── dataset_parte2.csv           # Catálogo Netflix — elencos (Parte 2)
├── out/                             # Saídas geradas (CSV, JSON, PNG, HTML)
│   ├── graus.csv
│   ├── ego_aeroportos.csv
│   ├── global.json
│   ├── regioes.json
│   ├── distancias_rotas.csv
│   ├── parte2_report.json           # Benchmarks de desempenho (Parte 2)
│   └── *.html / *.png               # Visualizações estáticas e interativas
├── src/
│   ├── solve.py                     # Script principal — roda tudo
│   ├── export_react.py              # Empacota dados para o front React
│   ├── viz.py                       # Todas as visualizações (matplotlib + plotly)
│   ├── cli.py                       # Interface de linha de comando
│   └── graphs/
│       ├── graph.py                 # Lista de adjacência (estrutura base)
│       ├── io.py                    # Leitura e normalização dos CSVs
│       ├── algorithms.py            # BFS, DFS, Dijkstra, Bellman-Ford
│       └── metrics.py               # Grau, densidade, ego-rede
├── dashboard/                       # App React (Vite)
│   ├── src/
│   │   ├── App.jsx
│   │   ├── Parte1.jsx
│   │   ├── Parte2.jsx
│   │   ├── data.js                  # Gerado pelo solve.py (Parte 1)
│   │   ├── data_parte2.js           # Gerado pelo solve.py (Parte 2)
│   │   ├── charts/
│   │   └── components/
│   └── package.json
└── tests/
    ├── test_bfs.py
    ├── test_dfs.py
    ├── test_dijkstra.py
    └── test_bellman_ford.py
```

---

## Pré-requisitos

- Python 3.10+
- Node.js 18+ e npm

### Dependências Python

```bash
pip install pandas matplotlib plotly numpy
```

### Dependências Node (apenas na primeira vez)

```bash
cd dashboard
npm install
```

---

## Como rodar

### 1. Gerar os dados e construir o dashboard

Na raiz do projeto:

```bash
python src/solve.py
```

Esse comando executa toda a pipeline:
- Constrói os grafos da Parte 1 e Parte 2
- Roda BFS, DFS, Dijkstra e Bellman-Ford
- Gera todos os arquivos em `out/` (CSV, JSON, PNG, HTML)
- Empacota os dados para o React (`dashboard/src/data.js` e `data_parte2.js`)
- Faz o build de produção do dashboard em `dashboard/dist/`

> O build React é feito automaticamente pelo `solve.py`. Não é necessário rodar `npm run build` manualmente.

### 2. Visualizar o dashboard

**Modo desenvolvimento** (com hot-reload):

```bash
cd dashboard
npm run dev
```

Abra [http://localhost:5173](http://localhost:5173) no navegador.

**Modo produção** (após o solve.py):

```bash
cd dashboard
npm run preview
```

> Sempre rode o `solve.py` antes do `npm run dev` — o dashboard lê os arquivos `data.js` e `data_parte2.js` que são gerados por ele.

---

## Rodando os testes

Na raiz do projeto:

```bash
python -m pytest tests/
```

Os testes cobrem BFS, DFS, Dijkstra e Bellman-Ford com grafos de diferentes tamanhos e estruturas.

---

## Dataset — Parte 1 (Aeroportos)

| Coluna | Descrição |
|---|---|
| `iata` | Código identificador do aeroporto (3 letras) |
| `cidade` | Cidade sede do aeroporto |
| `regiao` | Região do Brasil (Norte, Nordeste, Centro-Oeste, Sudeste, Sul) |

As arestas em `adjacencias_aeroportos.csv` classificam cada conexão como `regional`, `regional_hub` ou `hub_nacional`.

## Dataset — Parte 2 (Netflix)

`dataset_parte2.csv` contém o elenco de títulos do catálogo Netflix. Cada par de atores que aparece no mesmo título gera uma aresta na rede de colaboração.
