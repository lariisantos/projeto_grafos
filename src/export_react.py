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
