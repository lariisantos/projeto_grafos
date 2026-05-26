"""
Q10 -- Analise Exploratorio e Explanatoria dos Dados (AVD)

Gera 4 visualizacoes salvas em out/:
  Exploratorias:
    q10_exp1_distribuicao_graus.png  -- histograma + boxplot por regiao
    q10_exp2_grau_vs_densidade.png   -- grau x densidade da ego-rede
  Explanatorias:
    q10_expl1_ranking_hubs.png       -- ranking de conectividade dos aeroportos
    q10_expl2_comparacao_regioes.png -- painel comparativo entre regioes
"""

import json
import os

import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import pandas as pd

# Paleta de cores por regiao
CORES = {
    "Nordeste":     "#E63946",
    "Sudeste":      "#457B9D",
    "Sul":          "#2A9D8F",
    "Norte":        "#E9C46A",
    "Centro-Oeste": "#F4A261",
}

# ---------------------------------------------------------------------------
# Carga de dados
# ---------------------------------------------------------------------------

def _carregar(pasta_out: str, pasta_data: str):
    df_ego  = pd.read_csv(os.path.join(pasta_out,  "ego_aeroportos.csv"))
    df_aero = pd.read_csv(os.path.join(pasta_data, "aeroportos_data.csv"))
    df_adj  = pd.read_csv(os.path.join(pasta_data, "adjacencias_aeroportos.csv"))

    with open(os.path.join(pasta_out, "global.json"),  encoding="utf-8") as f:
        glob = json.load(f)
    with open(os.path.join(pasta_out, "regioes.json"), encoding="utf-8") as f:
        regioes = json.load(f)

    df_ego = (
        df_ego
        .merge(df_aero[["iata", "regiao"]], left_on="aeroporto", right_on="iata", how="left")
        .drop(columns="iata")
    )
    return df_ego, df_aero, df_adj, glob, regioes


# ---------------------------------------------------------------------------
# Exploratorio 1 -- Distribuicao dos graus
# ---------------------------------------------------------------------------

def _exp1_distribuicao(df_ego: pd.DataFrame, pasta: str) -> None:
    """Histograma de graus + boxplot por regiao."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle(
        "Exploratorio 1 - Distribuicao dos Graus na Rede de Aeroportos",
        fontsize=14, fontweight="bold", y=1.01,
    )

    # Histograma
    bins = range(df_ego["grau"].min(), df_ego["grau"].max() + 2)
    ax1.hist(df_ego["grau"], bins=bins,
             color="#457B9D", edgecolor="white", rwidth=0.72, alpha=0.9)

    media = df_ego["grau"].mean()
    ax1.axvline(media, color="#E63946", ls="--", lw=1.8,
                label=f"Media = {media:.1f}")
    ax1.set_xlabel("Grau (numero de conexoes diretas)", fontsize=11)
    ax1.set_ylabel("Numero de aeroportos", fontsize=11)
    ax1.set_title("Histograma dos graus", fontsize=12)
    ax1.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax1.legend(fontsize=10)
    ax1.grid(axis="y", alpha=0.3)

    # Boxplot por regiao
    regioes_ord = (
        df_ego.groupby("regiao")["grau"]
        .median()
        .sort_values(ascending=False)
        .index.tolist()
    )
    dados_box = [df_ego[df_ego["regiao"] == r]["grau"].values for r in regioes_ord]

    bp = ax2.boxplot(
        dados_box,
        patch_artist=True,
        medianprops=dict(color="black", linewidth=2.0),
        whiskerprops=dict(linewidth=1.2),
        capprops=dict(linewidth=1.2),
        flierprops=dict(marker="o", markerfacecolor="gray", markersize=5),
    )
    for patch, reg in zip(bp["boxes"], regioes_ord):
        patch.set_facecolor(CORES[reg])
        patch.set_alpha(0.8)

    ax2.set_xticklabels(regioes_ord, rotation=18, ha="right", fontsize=10)
    ax2.set_ylabel("Grau", fontsize=11)
    ax2.set_title("Distribuicao de graus por regiao", fontsize=12)
    ax2.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    caminho = os.path.join(pasta, "q10_exp1_distribuicao_graus.png")
    fig.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[Q10] Exploratorio 1 salvo -> {caminho}")


# ---------------------------------------------------------------------------
# Exploratorio 2 -- Composicao das conexoes por tipo (stacked bar)
# ---------------------------------------------------------------------------

def _exp2_composicao_conexoes(
    df_ego: pd.DataFrame,
    df_adj: pd.DataFrame,
    pasta: str,
) -> None:
    """
    Barra empilhada: para cada aeroporto mostra quantas conexoes sao
    'regional', 'regional_hub' ou 'hub_nacional'.
    Ordenado pelo grau total (maior para menor).
    Permite explorar a estrutura interna de cada no sem pressupor mensagem.
    """
    TIPOS = ["regional", "regional_hub", "hub_nacional"]
    CORES_TIPO = {
        "regional":      "#A8DADC",
        "regional_hub":  "#457B9D",
        "hub_nacional":  "#E63946",
    }

    # Contar arestas por tipo em cada aeroporto (grafo nao-direcionado)
    contagem: dict[str, dict[str, int]] = {}
    for _, row in df_adj.iterrows():
        for no in [row["origem"], row["destino"]]:
            if no not in contagem:
                contagem[no] = {t: 0 for t in TIPOS}
            contagem[no][row["tipo_conexao"]] += 1

    df_cont = (
        pd.DataFrame(contagem).T
        .reset_index()
        .rename(columns={"index": "aeroporto"})
        .merge(df_ego[["aeroporto", "regiao", "grau"]], on="aeroporto")
        .sort_values("grau", ascending=False)
    )
    # garantir colunas de tipo existam
    for t in TIPOS:
        if t not in df_cont.columns:
            df_cont[t] = 0

    fig, ax = plt.subplots(figsize=(14, 5))

    bottom = [0.0] * len(df_cont)
    for tipo in TIPOS:
        valores = df_cont[tipo].fillna(0).tolist()
        bars = ax.bar(
            df_cont["aeroporto"], valores,
            bottom=bottom,
            color=CORES_TIPO[tipo],
            edgecolor="white", linewidth=0.5,
            label=tipo.replace("_", " ").capitalize(),
        )
        bottom = [b + v for b, v in zip(bottom, valores)]

    # Rotulo de grau total em cima de cada barra
    for i, (_, row) in enumerate(df_cont.iterrows()):
        ax.text(
            i, row["grau"] + 0.15,
            str(int(row["grau"])),
            ha="center", va="bottom", fontsize=8, color="#333333",
        )

    # Colorir os labels do eixo X por regiao
    ax.set_xticks(range(len(df_cont)))
    ax.set_xticklabels(df_cont["aeroporto"], rotation=45, ha="right", fontsize=9)
    for tick, (_, row) in zip(ax.get_xticklabels(), df_cont.iterrows()):
        tick.set_color(CORES.get(row["regiao"], "#333333"))
        tick.set_fontweight("bold")

    # Legenda de tipos de aresta
    ax.legend(title="Tipo de conexao", fontsize=9, title_fontsize=9,
              loc="upper right")

    # Legenda de regioes (via patches extras)
    patches = [mpatches.Patch(color=c, label=r) for r, c in CORES.items()]
    leg2 = ax.legend(handles=patches, title="Regiao (cor do label)",
                     fontsize=8, title_fontsize=8,
                     loc="upper center", ncol=5,
                     bbox_to_anchor=(0.5, -0.22))
    ax.add_artist(leg2)
    # recolocar a primeira legenda
    ax.legend(title="Tipo de conexao", fontsize=9, title_fontsize=9,
              loc="upper right")

    ax.set_ylabel("Numero de conexoes", fontsize=11)
    ax.set_title(
        "Exploratorio 2 - Composicao das Conexoes por Tipo em Cada Aeroporto\n"
        "Hubs nacionais acumulam os tres tipos; aeroportos internos so tem conexoes regionais",
        fontsize=12, fontweight="bold",
    )
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    caminho = os.path.join(pasta, "q10_exp2_grau_vs_densidade.png")
    fig.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[Q10] Exploratorio 2 salvo -> {caminho}")


# ---------------------------------------------------------------------------
# Explanatorio 1 -- Ranking de conectividade (hubs)
# ---------------------------------------------------------------------------

def _expl1_ranking_hubs(df_ego: pd.DataFrame, pasta: str) -> None:
    """
    Barras horizontais com grau de cada aeroporto, colorido por regiao.
    Mensagem principal: quem sao os hubs nacionais.
    """
    df_sorted = df_ego.sort_values("grau", ascending=True)

    fig, ax = plt.subplots(figsize=(11, 7))

    colors = [CORES[r] for r in df_sorted["regiao"]]
    bars = ax.barh(
        df_sorted["aeroporto"], df_sorted["grau"],
        color=colors, edgecolor="white", height=0.65,
    )

    # Rotulo de valor ao lado de cada barra
    for bar in bars:
        w = bar.get_width()
        ax.text(
            w + 0.08, bar.get_y() + bar.get_height() / 2,
            str(int(w)), va="center", ha="left",
            fontsize=10, fontweight="bold", color="#222222",
        )

    # Linha da media global
    media = df_ego["grau"].mean()
    ax.axvline(media, color="#555555", ls="--", lw=1.5,
               label=f"Media da rede: {media:.1f} conexoes")

    # Legenda de regioes
    patches = [mpatches.Patch(color=c, label=r) for r, c in CORES.items()]
    ax.legend(handles=patches, title="Regiao", fontsize=9,
              title_fontsize=9, loc="lower right")

    ax.set_xlabel("Grau - numero de conexoes diretas na rede", fontsize=11)
    ax.set_title(
        "Explanatorio 1 - Quais aeroportos sao os maiores hubs da rede?\n"
        "REC (Recife) e GRU (Sao Paulo) concentram o maior numero de conexoes",
        fontsize=12, fontweight="bold",
    )
    ax.set_xlim(0, df_ego["grau"].max() + 1.8)
    ax.grid(axis="x", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    caminho = os.path.join(pasta, "q10_expl1_ranking_hubs.png")
    fig.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[Q10] Explanatorio 1 salvo -> {caminho}")


# ---------------------------------------------------------------------------
# Explanatorio 2 -- Comparacao entre regioes
# ---------------------------------------------------------------------------

def _expl2_comparacao_regioes(
    df_ego: pd.DataFrame,
    regioes: list,
    pasta: str,
) -> None:
    """
    Tres subplots: num. aeroportos, arestas internas e grau medio por regiao.
    Comunica disparidades estruturais de forma auto-explicada.
    """
    df_r = pd.DataFrame(regioes)

    grau_medio = (
        df_ego.groupby("regiao")["grau"]
        .mean()
        .rename("grau_medio")
        .reset_index()
    )
    df_r = df_r.merge(grau_medio, on="regiao")

    metricas = [
        ("ordem",      "No. de aeroportos",     "Aeroportos\npor regiao"),
        ("tamanho",    "No. de arestas internas", "Arestas internas\npor regiao"),
        ("grau_medio", "Grau medio",             "Grau medio dos\naeroportos"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(
        "Explanatorio 2 - Como as regioes do Brasil se comparam na rede?\n"
        "Nordeste lidera em volume; Sudeste e Norte concentram os maiores hubs",
        fontsize=12, fontweight="bold", y=1.03,
    )

    for ax, (col, ylabel, title) in zip(axes, metricas):
        df_plot = df_r.sort_values(col, ascending=False)
        colors  = [CORES[r] for r in df_plot["regiao"]]

        bars = ax.bar(
            df_plot["regiao"], df_plot[col],
            color=colors, edgecolor="white", width=0.55,
        )

        for bar in bars:
            h = bar.get_height()
            label = f"{h:.1f}" if col == "grau_medio" else str(int(h))
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + df_plot[col].max() * 0.02,
                label, ha="center", va="bottom",
                fontsize=11, fontweight="bold",
            )

        ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_xticks(range(len(df_plot["regiao"])))
        ax.set_xticklabels(df_plot["regiao"], rotation=22, ha="right", fontsize=9)
        ax.set_ylim(0, df_plot[col].max() * 1.22)
        ax.grid(axis="y", alpha=0.3)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    plt.tight_layout()
    caminho = os.path.join(pasta, "q10_expl2_comparacao_regioes.png")
    fig.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[Q10] Explanatorio 2 salvo -> {caminho}")


# ---------------------------------------------------------------------------
# Relatorio textual no terminal (apenas ASCII para compatibilidade Windows)
# ---------------------------------------------------------------------------

def _relatorio(df_ego: pd.DataFrame, glob: dict, regioes: list) -> None:
    sep = "=" * 58
    print(f"\n[Q10] {sep}")
    print("[Q10]  ANALISE EXPLORATORIA E EXPLANATORIA -- Q10")
    print(f"[Q10] {sep}")

    print("\n[Q10] -- Metricas Globais -----------------------------------")
    print(f"  Ordem (vertices) : {glob['ordem']}")
    print(f"  Tamanho (arestas): {glob['tamanho']}")
    print(f"  Densidade global : {glob['densidade']:.4f}  (rede esparsa)")
    print(f"  Grau medio       : {df_ego['grau'].mean():.2f}")
    print(f"  Grau maximo (hub): {df_ego['grau'].max()} - "
          f"{df_ego.loc[df_ego['grau'].idxmax(), 'aeroporto']}")
    print(f"  Grau minimo      : {df_ego['grau'].min()} - "
          f"{df_ego.loc[df_ego['grau'].idxmin(), 'aeroporto']}")

    print("\n[Q10] -- Metricas por Regiao --------------------------------")
    for r in sorted(regioes, key=lambda x: x["ordem"], reverse=True):
        gm = df_ego[df_ego["regiao"] == r["regiao"]]["grau"].mean()
        print(f"  {r['regiao']:15s} | aeroportos={r['ordem']:2d} "
              f"| arestas internas={r['tamanho']:3d} "
              f"| densidade={r['densidade']:.4f} "
              f"| grau medio={gm:.2f}")

    media = df_ego["grau"].mean()
    std   = df_ego["grau"].std()
    hubs  = (
        df_ego[df_ego["grau"] >= media + std]
        .sort_values("grau", ascending=False)
    )
    print(f"\n[Q10] -- Hubs (grau >= media + 1 desvio = {media + std:.1f}) -----")
    for _, h in hubs.iterrows():
        print(f"  {h['aeroporto']} ({h['regiao']:15s}) grau={h['grau']}, "
              f"dens_ego={h['densidade_ego']:.3f}")

    print("\n[Q10] -- Padroes Identificados ------------------------------")
    print("  * Todas as regioes formam subgrafos completos (densidade=1.0).")
    print("  * Densidade global (0.2368): poucas conexoes inter-regionais.")
    print("  * Hubs nacionais (REC,GRU,MAO,POA,BSB) conectam as regioes.")
    print("  * Aeroportos com alto grau tendem a ter menor densidade ego-rede.")
    print("  * GYN (Goiania) e o unico aeroporto com grau 1 -- periferico.")
    print(f"[Q10] {sep}\n")


# ---------------------------------------------------------------------------
# Ponto de entrada publico
# ---------------------------------------------------------------------------

def analise_avd(
    pasta_saida: str = "out",
    pasta_data:  str = "data",
) -> None:
    """Executa toda a analise AVD do Q10 e salva as visualizacoes."""
    os.makedirs(pasta_saida, exist_ok=True)

    df_ego, _, df_adj, glob, regioes = _carregar(pasta_saida, pasta_data)

    _relatorio(df_ego, glob, regioes)

    _exp1_distribuicao(df_ego, pasta_saida)
    _exp2_composicao_conexoes(df_ego, df_adj, pasta_saida)
    _expl1_ranking_hubs(df_ego, pasta_saida)
    _expl2_comparacao_regioes(df_ego, regioes, pasta_saida)

    print("[Q10] Analise AVD concluida -- 4 visualizacoes geradas em out/\n")
