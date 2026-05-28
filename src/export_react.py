"""
Exporta dados para o app React em dashboard/src/data.js
e copia os HTMLs das redes para dashboard/public/.
"""
import csv
import json
import os
import shutil
import subprocess
import sys

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
    with open(os.path.join(DATA, "aeroportos_data.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            regioes_map[row["iata"]] = row["regiao"]
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

    return glob, regioes, ego, adj


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


def exportar_react_data():
    os.makedirs(DASH_SRC, exist_ok=True)
    os.makedirs(DASH_PUB, exist_ok=True)

    glob, regioes, ego, adj = _load()
    hist_data, reg_data, composicao, hubs, regioes_chart = _compute_charts(
        glob, regioes, ego, adj
    )

    payload = {
        "global":        glob,
        "regioes":       regioes_chart,
        "egoAeroportos": ego,
        "histData":      hist_data,
        "regData":       reg_data,
        "composicao":    composicao,
        "hubs":          hubs,
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
