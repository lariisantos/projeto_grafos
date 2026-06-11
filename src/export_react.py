"""
Exporta dados para o app React em dashboard/src/data.js
e copia os HTMLs das redes para dashboard/public/.
"""
import csv
import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np

# Paleta usada para colorir cada percurso no RouteTree
ROTA_CORES = ["#3b82f6", "#ff4d6d", "#2dd4bf", "#fbbf24", "#a78bfa", "#f97316", "#34d399", "#f472b6"]

BASE     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT      = os.path.join(BASE, "out")
DATA     = os.path.join(BASE, "data")
DASH_SRC = os.path.join(BASE, "dashboard", "src")
DASH_PUB = os.path.join(BASE, "dashboard", "public")
DASH_DIR = os.path.join(BASE, "dashboard")


def _load():
    with open(os.path.join(OUT, "global.json"),  encoding="utf-8") as f: glob    = json.load(f)
    with open(os.path.join(OUT, "regioes.json"), encoding="utf-8") as f: regioes = json.load(f)

    ego = []
    with open(os.path.join(OUT, "ego_aeroportos.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ego.append({
                "aeroporto":    row["aeroporto"],
                "grau":         int(row["grau"]),
                "ordem_ego":    int(row["ordem_ego"]),
                "tamanho_ego":  int(row["tamanho_ego"]),
                "densidade_ego": float(row["densidade_ego"]),
            })

    # adiciona regiao ao ego
    regioes_map = {}
    cidades_map = {}
    with open(os.path.join(DATA, "aeroportos_data.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            regioes_map[row["iata"]] = row["regiao"]
            cidades_map[row["iata"]] = row["cidade"]
    for a in ego:
        a["regiao"] = regioes_map.get(a["aeroporto"], "Desconhecida")

    adj = []
    with open(os.path.join(DATA, "adjacencias_aeroportos.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            adj.append({
                "origem":          row["origem"],
                "destino":         row["destino"],
                "tipo_conexao":    row["tipo_conexao"],
                "peso":            float(row["peso"]),
            })

    return glob, regioes, ego, adj, regioes_map, cidades_map


def _compute_charts(glob, regioes, ego, adj):
    # Histogram
    from collections import Counter
    hist_raw = Counter(a["grau"] for a in ego)
    hist_data = [{"grau": g, "count": c} for g, c in sorted(hist_raw.items())]

    # Media por regiao
    from collections import defaultdict
    reg_graus = defaultdict(list)
    for a in ego:
        reg_graus[a["regiao"]].append(a["grau"])
    reg_data = [
        {"regiao": r, "media": round(sum(v)/len(v), 2)}
        for r, v in sorted(reg_graus.items())
    ]

    # Composicao por tipo
    TIPOS_MAP = {"regional": "Regional", "regional_hub": "Hub regional", "hub_nacional": "Hub nacional"}
    cont = {}
    for row in adj:
        for no in [row["origem"], row["destino"]]:
            if no not in cont:
                cont[no] = {"Regional": 0, "Hub regional": 0, "Hub nacional": 0}
            tipo_pt = TIPOS_MAP.get(row["tipo_conexao"], row["tipo_conexao"])
            if tipo_pt in cont[no]:
                cont[no][tipo_pt] += 1

    grau_map = {a["aeroporto"]: a["grau"] for a in ego}
    regiao_map = {a["aeroporto"]: a["regiao"] for a in ego}
    composicao = sorted([
        {
            "aeroporto": no,
            "Regional": v["Regional"],
            "Hub regional": v["Hub regional"],
            "Hub nacional": v["Hub nacional"],
            "regiao": regiao_map.get(no, ""),
            "grau": grau_map.get(no, 0),
        }
        for no, v in cont.items()
    ], key=lambda x: -x["grau"])

    # Hubs ranking
    hubs = sorted(
        [{"aeroporto": a["aeroporto"], "grau": a["grau"],
          "regiao": a["regiao"], "densidade_ego": a["densidade_ego"]}
         for a in ego],
        key=lambda x: x["grau"]
    )

    # Regioes painel – adiciona grau_medio
    grau_medio_map = {r["regiao"]: round(sum(v)/len(v), 2) for r, v in
                      zip(reg_data, [reg_graus[r["regiao"]] for r in reg_data])}
    regioes_chart = [
        {**r, "grau_medio": grau_medio_map.get(r["regiao"], 0)}
        for r in regioes
    ]

    return hist_data, reg_data, composicao, hubs, regioes_chart


def _build_grafo_dados(ego, adj, cidades_map):
    """Monta {nodes, edges} para o componente NetworkGraph."""
    nodes = [
        {
            "id":           a["aeroporto"],
            "regiao":       a["regiao"],
            "cidade":       cidades_map.get(a["aeroporto"], ""),
            "grau":         a["grau"],
            "densidadeEgo": a["densidade_ego"],
        }
        for a in ego
    ]
    edges = [
        {
            "source": e["origem"],
            "target": e["destino"],
            "tipo":   e["tipo_conexao"],
            "peso":   e["peso"],
        }
        for e in adj
    ]
    return {"nodes": nodes, "edges": edges}


def _build_percursos_dados(regioes_map, cidades_map, adj):
    """Monta {nodes, edges, caminhos} para o componente RouteTree.

    Lê os caminhos minimos ja calculados em out/distancias_rotas.csv e
    posiciona os nos envolvidos em um layout circular (x/y fixos)."""
    # peso de cada aresta (nao-direcionado)
    peso_map = {frozenset((e["origem"], e["destino"])): e["peso"] for e in adj}

    caminhos = []
    csv_path = os.path.join(OUT, "distancias_rotas.csv")
    if os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if "->" not in row["caminho"]:
                    continue  # rota sem caminho viavel
                seq = [p.strip() for p in row["caminho"].split("->")]
                caminhos.append({
                    "origem":  row["origem"],
                    "destino": row["destino"],
                    "caminho": seq,
                    "custo":   float(row["custo"]),
                    "cor":     ROTA_CORES[len(caminhos) % len(ROTA_CORES)],
                })

    # nos unicos, na ordem em que aparecem
    node_ids = []
    for c in caminhos:
        for nid in c["caminho"]:
            if nid not in node_ids:
                node_ids.append(nid)

    # layout circular
    W, H = 800, 460
    cx, cy, R = W / 2, H / 2, min(W, H) * 0.36
    total = max(len(node_ids), 1)
    nodes = []
    for idx, nid in enumerate(node_ids):
        angle = (idx / total) * 2 * math.pi - math.pi / 2
        nodes.append({
            "id":     nid,
            "x":      round(cx + R * math.cos(angle), 1),
            "y":      round(cy + R * math.sin(angle), 1),
            "regiao": regioes_map.get(nid, "Desconhecida"),
            "label":  cidades_map.get(nid, ""),
        })

    # arestas dos trechos consecutivos de cada caminho
    edges, seen = [], set()
    for c in caminhos:
        for a, b in zip(c["caminho"], c["caminho"][1:]):
            if (a, b) in seen:
                continue
            seen.add((a, b))
            edges.append({
                "source": a,
                "target": b,
                "color":  c["cor"],
                "weight": peso_map.get(frozenset((a, b)), 1.0),
            })

    return {"nodes": nodes, "edges": edges, "caminhos": caminhos}


def exportar_react_data():
    os.makedirs(DASH_SRC, exist_ok=True)
    os.makedirs(DASH_PUB, exist_ok=True)

    glob, regioes, ego, adj, regioes_map, cidades_map = _load()
    hist_data, reg_data, composicao, hubs, regioes_chart = _compute_charts(
        glob, regioes, ego, adj
    )
    grafo_dados     = _build_grafo_dados(ego, adj, cidades_map)
    percursos_dados = _build_percursos_dados(regioes_map, cidades_map, adj)

    payload = {
        "global":         glob,
        "regioes":        regioes_chart,
        "egoAeroportos":  ego,
        "histData":       hist_data,
        "regData":        reg_data,
        "composicao":     composicao,
        "hubs":           hubs,
        "grafoDados":     grafo_dados,
        "percursosDados": percursos_dados,
    }
    data_js = (
        "// Gerado automaticamente por export_react.py -- nao edite manualmente\n"
        f"export const DATA = {json.dumps(payload, ensure_ascii=False, indent=2)};\n"
    )

    dest = os.path.join(DASH_SRC, "data.js")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(data_js)
    print(f"[REACT] data.js gerado -> {dest}")

    # copia HTMLs das redes para public/
    for fname in ("arvore_percurso.html", "grafo_interativo.html"):
        src = os.path.join(OUT, fname)
        dst = os.path.join(DASH_PUB, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"[REACT] copiado {fname} -> public/")


# ──────────────────────────────────────────────────────────────────────────
# PARTE 2 — Rede de colaboração de atores (Netflix)
# O grafo é grande demais para exportar inteiro; exportamos apenas agregados
# compactos para o front React (histograma, ranking, heatmap e amostra do grafo).
# ──────────────────────────────────────────────────────────────────────────
def _bfs_dist(adj, origem):
    """Distâncias em nº de saltos (BFS) a partir de `origem`."""
    from collections import deque
    dist = {origem: 0}
    fila = deque([origem])
    while fila:
        no = fila.popleft()
        for viz in adj.get(no, {}):
            if viz not in dist:
                dist[viz] = dist[no] + 1
                fila.append(viz)
    return dist


def _params_histograma(grau_max, n_bins=12):
    """Largura da faixa e índice do último bin, dado o grau máximo GLOBAL.
    Usado para que todos os histogramas (geral + por gênero) compartilhem o
    mesmo eixo X, ficando comparáveis."""
    largura = max(1, math.ceil((grau_max + 1) / n_bins))
    b_max = grau_max // largura
    return largura, b_max


def _histograma_de_graus(valores, largura, b_max):
    """Monta as faixas [{faixa, ini, count}] a partir de uma lista de graus."""
    faixas = {}
    for d in valores:
        faixas[d // largura] = faixas.get(d // largura, 0) + 1
    out = []
    for b in range(b_max + 1):
        ini, fim = b * largura, b * largura + largura - 1
        out.append({"faixa": f"{ini}–{fim}", "ini": ini, "count": faixas.get(b, 0)})
    return out


def _build_generos_dados(grafo, caminho_dataset, top_generos=12, top_ranking=20):
    """Filtro por GÊNERO para os gráficos da Parte 2.

    O gênero é um filtro de PERTENCIMENTO ("atores de comédia/drama…"): o grau
    continua sendo o nº global de colaboradores; só muda QUEM aparece. Lê os
    gêneros (`listed_in`) e o elenco (`cast`) direto do CSV, sem mexer no grafo.
    Para cada gênero do topo (por nº de atores) gera ranking + histograma."""
    graus = {no: len(viz) for no, viz in grafo.adj.items()}

    # gênero -> conjunto de atores que aparecem em pelo menos um título do gênero
    genero_atores: dict[str, set] = {}
    with open(caminho_dataset, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cast = [a.strip() for a in (row.get("cast") or "").split(",") if a.strip()]
            gens = [g.strip() for g in (row.get("listed_in") or "").split(",") if g.strip()]
            if not cast or not gens:
                continue
            for g in gens:
                alvo = genero_atores.setdefault(g, set())
                for a in cast:
                    if a in graus:
                        alvo.add(a)

    top = sorted(genero_atores, key=lambda g: len(genero_atores[g]), reverse=True)[:top_generos]

    grau_max = max(graus.values()) if graus else 0
    largura, b_max = _params_histograma(grau_max)

    ranking, histograma, contagem = {}, {}, {}
    for g in top:
        atores = genero_atores[g]
        ordenados = sorted(atores, key=lambda a: graus[a], reverse=True)[:top_ranking]
        ranking[g] = [{"ator": a, "grau": graus[a]} for a in ordenados]
        histograma[g] = _histograma_de_graus([graus[a] for a in atores], largura, b_max)
        contagem[g] = len(atores)

    return {"lista": top, "ranking": ranking, "histograma": histograma, "contagem": contagem}


def _build_parte2_dados(grafo, top_ranking=20, top_heatmap=12, ego_vizinhos=22):
    graus = {no: len(viz) for no, viz in grafo.adj.items()}
    n = len(graus)
    m = sum(graus.values()) // 2
    grau_medio = (sum(graus.values()) / n) if n else 0
    densidade = (2 * m / (n * (n - 1))) if n > 1 else 0
    ator_top = max(graus, key=graus.get) if graus else None
    ator_top_grau = graus.get(ator_top, 0)

    # Histograma — faixas lineares de grau (mesmo binning dos gêneros)
    grau_max = max(graus.values()) if graus else 0
    largura, b_max = _params_histograma(grau_max)
    histograma = _histograma_de_graus(graus.values(), largura, b_max)

    # Ranking dos atores mais conectados
    ordenados = sorted(graus.items(), key=lambda kv: kv[1], reverse=True)
    ranking = [{"ator": a, "grau": d} for a, d in ordenados[:top_ranking]]

    # Heatmap de distâncias (saltos BFS) entre os top atores
    top_hm = [a for a, _ in ordenados[:top_heatmap]]
    matriz = []
    for a in top_hm:
        dist = _bfs_dist(grafo.adj, a)
        matriz.append([dist.get(b) for b in top_hm])  # None = sem caminho (componentes distintas)
    heatmap = {"atores": top_hm, "matriz": matriz}

    # Amostra do grafo — ego-rede do ator mais conectado (centro + vizinhos por peso)
    rede = {"nodes": [], "edges": []}
    if ator_top:
        vizinhos = sorted(grafo.adj[ator_top].items(), key=lambda kv: kv[1], reverse=True)[:ego_vizinhos]
        selecionados = [ator_top] + [v for v, _ in vizinhos]
        sel_set = set(selecionados)
        rede["nodes"] = [{"id": a, "grau": graus[a], "centro": a == ator_top} for a in selecionados]
        visto = set()
        for u in selecionados:
            for v, peso in grafo.adj[u].items():
                if v in sel_set:
                    chave = tuple(sorted((u, v)))
                    if chave not in visto:
                        visto.add(chave)
                        rede["edges"].append({"source": u, "target": v, "peso": peso})

    return {
        "resumo": {
            "ordem": n,
            "tamanho": m,
            "grauMedio": round(grau_medio, 2),
            "grauMax": grau_max,
            "densidade": densidade,
            "atorTop": ator_top,
            "atorTopGrau": ator_top_grau,
        },
        "histograma": histograma,
        "ranking": ranking,
        "heatmap": heatmap,
        "rede": rede,
    }


def exportar_react_data_parte2(grafo, caminho_dataset=os.path.join(DATA, "dataset_parte2.csv")):
    """Exporta os agregados da Parte 2 para dashboard/src/data_parte2.js."""
    os.makedirs(DASH_SRC, exist_ok=True)
    payload = _build_parte2_dados(grafo)

    # filtro por gênero (ranking + histograma); "Todos" reaproveita o global
    generos = _build_generos_dados(grafo, caminho_dataset)
    generos["lista"] = ["Todos"] + generos["lista"]
    generos["ranking"]["Todos"] = payload["ranking"]
    generos["histograma"]["Todos"] = payload["histograma"]
    payload["generos"] = generos

    data_js = (
        "// Gerado automaticamente por export_react.py -- nao edite manualmente\n"
        f"export const DATA_PARTE2 = {json.dumps(payload, ensure_ascii=False, indent=2)};\n"
    )
    dest = os.path.join(DASH_SRC, "data_parte2.js")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(data_js)
    print(f"[REACT] data_parte2.js gerado -> {dest} "
          f"(ranking={len(payload['ranking'])}, generos={len(generos['lista'])}, "
          f"rede={len(payload['rede']['nodes'])} nós)")


# ──────────────────────────────────────────────────────────────────────────
# Layout 2D do grafo INTEIRO (para o Canvas do front desenhar TODOS os nós).
# Fruchterman-Reingold acelerado por grade: a repulsão é aproximada por
# centróides de célula (Barnes-Hut simplificado) -> O(n) por iteração, sem
# matriz n×n. numpy vetoriza atração (bincount) e o passo de integração.
# ──────────────────────────────────────────────────────────────────────────
def _layout_forcas(grafo, iteracoes=120, seed=42, grav=0.06):
    ids = list(grafo.adj.keys())
    idx = {a: i for i, a in enumerate(ids)}
    N = len(ids)

    s, d = [], []
    for a in ids:
        ia = idx[a]
        for b in grafo.adj[a]:
            ib = idx[b]
            if ia < ib:
                s.append(ia); d.append(ib)
    src = np.asarray(s, dtype=np.int64)
    dst = np.asarray(d, dtype=np.int64)

    rng = np.random.default_rng(seed)
    W = 1000.0
    pos = rng.uniform(0, W, size=(N, 2))
    k = 0.9 * W / math.sqrt(max(N, 1))       # distância ótima entre nós
    t = W * 0.10                              # temperatura (passo máximo)
    cooling = t / (iteracoes + 1)
    G = max(10, int(math.sqrt(N) / 4))        # resolução da grade
    eps = 1e-4

    for _ in range(iteracoes):
        disp = np.zeros((N, 2))

        # repulsão: cada célula ocupada age como um supernó (centróide × contagem)
        mn = pos.min(axis=0)
        span = np.maximum(pos.max(axis=0) - mn, eps)
        cell = ((pos - mn) / span * (G - 1e-6)).astype(np.int64)
        cid = cell[:, 0] * G + cell[:, 1]
        ncell = G * G
        cnt = np.bincount(cid, minlength=ncell).astype(np.float64)
        sx = np.bincount(cid, weights=pos[:, 0], minlength=ncell)
        sy = np.bincount(cid, weights=pos[:, 1], minlength=ncell)
        occ = np.nonzero(cnt)[0]
        cx, cy, cw = sx[occ] / cnt[occ], sy[occ] / cnt[occ], cnt[occ]
        for j in range(len(occ)):
            dx = pos[:, 0] - cx[j]
            dy = pos[:, 1] - cy[j]
            d2 = dx * dx + dy * dy + eps
            f = cw[j] * (k * k) / d2
            disp[:, 0] += f * dx
            disp[:, 1] += f * dy

        # atração ao longo das arestas (vetorizado via bincount)
        if src.size:
            delta = pos[dst] - pos[src]
            dist = np.sqrt((delta * delta).sum(axis=1)) + eps
            fa = (dist * dist) / k
            cont = delta / dist[:, None] * fa[:, None]
            disp[:, 0] += (np.bincount(src, weights=cont[:, 0], minlength=N)
                           - np.bincount(dst, weights=cont[:, 0], minlength=N))
            disp[:, 1] += (np.bincount(src, weights=cont[:, 1], minlength=N)
                           - np.bincount(dst, weights=cont[:, 1], minlength=N))

        # gravidade em direção ao centro: impede nós pouco conectados de voarem
        C = pos.mean(axis=0)
        disp += grav * (C - pos)

        # limita o passo pela temperatura e aplica
        dlen = np.sqrt((disp * disp).sum(axis=1)) + eps
        pos += disp * (np.minimum(dlen, t) / dlen)[:, None]
        t = max(t - cooling, 0.0)

    return pos, ids, src, dst


def exportar_grafo_render_json(grafo, nome_arquivo="grafo_parte2_15k.json", n_labels=24):
    """Calcula o layout do grafo inteiro e grava um JSON compacto em public/
    com posições + arestas, para o Canvas do front desenhar TODOS os nós."""
    os.makedirs(DASH_PUB, exist_ok=True)
    pos, ids, src, dst = _layout_forcas(grafo)
    N = len(ids)
    graus = [len(grafo.adj[a]) for a in ids]

    # normaliza pelo intervalo 1–99% (robusto a outliers): o núcleo ocupa
    # ~0..1000 e nós distantes caem fora dessa faixa (alcançáveis com zoom-out)
    lo, hi = np.percentile(pos, 1, axis=0), np.percentile(pos, 99, axis=0)
    span = np.where((hi - lo) < 1e-6, 1.0, (hi - lo))
    coords = ((pos - lo) / span * 1000).round().astype(int)

    labels = sorted(range(N), key=lambda i: graus[i], reverse=True)[:n_labels]
    payload = {
        "meta": {"n": N, "m": int(src.size), "grauMax": int(max(graus)) if graus else 0},
        "ids": ids,
        "g": graus,
        "x": coords[:, 0].tolist(),
        "y": coords[:, 1].tolist(),
        "edges": np.column_stack([src, dst]).astype(int).ravel().tolist(),
        "labels": labels,
    }
    dest = os.path.join(DASH_PUB, nome_arquivo)
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print(f"[REACT] {nome_arquivo} gerado -> {dest} "
          f"(N={N}, M={src.size}, {os.path.getsize(dest) / 1024:.0f} KB)")
    return dest


def buildar_react():
    print("[REACT] Instalando dependencias (se necessario)...")
    subprocess.run(
        ["npm", "install", "--prefer-offline"],
        cwd=DASH_DIR, check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        shell=True,
    )
    print("[REACT] Buildando app React...")
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=DASH_DIR, capture_output=True, text=True, shell=True,
    )
    if result.returncode != 0:
        print("[REACT] Erro no build:")
        print(result.stderr)
        raise RuntimeError("npm run build falhou")
    print(f"[REACT] Build concluido -> dashboard/dist/index.html")


if __name__ == "__main__":
    exportar_react_data()
    buildar_react()
