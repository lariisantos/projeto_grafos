"""
Q10 -- Analise Exploratorio e Explanatoria dos Dados (AVD)

Gera 4 visualizacoes interativas salvas em out/:
  Exploratorias:
    q10_exp1_distribuicao_graus.html  -- histograma + boxplot por regiao
    q10_exp2_composicao_conexoes.html -- composicao das conexoes por tipo
  Explanatorias:
    q10_expl1_ranking_hubs.html       -- ranking de conectividade dos aeroportos
    q10_expl2_comparacao_regioes.html -- painel comparativo entre regioes
"""

import json
import os

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

CORES = {
    "Nordeste":     "#E63946",
    "Sudeste":      "#457B9D",
    "Sul":          "#2A9D8F",
    "Norte":        "#E9C46A",
    "Centro-Oeste": "#F4A261",
}

CORES_TIPO = {
    "regional":     "#A8DADC",
    "regional_hub": "#457B9D",
    "hub_nacional": "#E63946",
}

LAYOUT_BASE = dict(
    paper_bgcolor="#07111f",
    plot_bgcolor="#0f1e35",
    font=dict(family="Inter, Segoe UI, Arial, sans-serif", color="#e5eefc"),
    title_font=dict(size=18, color="#f0f9ff"),
    legend=dict(
        bgcolor="rgba(15,23,42,0.85)",
        bordercolor="rgba(148,163,184,0.3)",
        borderwidth=1,
    ),
    margin=dict(t=90, b=60, l=60, r=40),
    hoverlabel=dict(
        bgcolor="#0f172a",
        bordercolor="rgba(148,163,184,0.4)",
        font=dict(color="#e5eefc", size=13),
    ),
)


def _carregar(pasta_out, pasta_data):
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


def _salvar_html(fig, caminho, titulo_log):
    fig.write_html(caminho, include_plotlyjs="cdn", full_html=True,
                   config={"displayModeBar": True, "scrollZoom": True})
    print(f"[Q10] {titulo_log} salvo -> {caminho}")


def _exp1_distribuicao(df_ego, pasta):
    regioes_ord = (
        df_ego.groupby("regiao")["grau"]
        .median().sort_values(ascending=False).index.tolist()
    )
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Histograma dos graus",
                                        "Distribuicao por regiao"),
                        horizontal_spacing=0.12)

    fig.add_trace(go.Histogram(
        x=df_ego["grau"], name="Aeroportos",
        marker=dict(color="#457B9D", line=dict(color="#07111f", width=1)),
        opacity=0.9,
        hovertemplate="Grau %{x}: %{y} aeroportos<extra></extra>",
    ), row=1, col=1)

    media = df_ego["grau"].mean()
    fig.add_vline(x=media, line=dict(color="#E63946", dash="dash", width=2),
                  annotation_text=f"Media = {media:.1f}",
                  annotation_font=dict(color="#E63946"), row=1, col=1)

    for reg in regioes_ord:
        fig.add_trace(go.Box(
            y=df_ego[df_ego["regiao"] == reg]["grau"],
            name=reg, marker_color=CORES[reg], line_color=CORES[reg], boxmean=True,
            hovertemplate=f"<b>{reg}</b><br>Grau: %{{y}}<extra></extra>",
        ), row=1, col=2)

    fig.update_layout(**LAYOUT_BASE, height=520, showlegend=True,
                      title=dict(text="Exploratorio 1 - Distribuicao dos Graus na Rede",
                                 x=0.5, xanchor="center"))
    for col, xt, yt in [(1, "Grau", "Qtd aeroportos"), (2, "Regiao", "Grau")]:
        fig.update_xaxes(title_text=xt, gridcolor="rgba(148,163,184,0.1)", row=1, col=col)
        fig.update_yaxes(title_text=yt, gridcolor="rgba(148,163,184,0.1)", row=1, col=col)

    _salvar_html(fig, os.path.join(pasta, "q10_exp1_distribuicao_graus.html"), "Exploratorio 1")


def _exp2_composicao_conexoes(df_ego, df_adj, pasta):
    TIPOS = ["regional", "regional_hub", "hub_nacional"]
    contagem = {}
    for _, row in df_adj.iterrows():
        for no in [row["origem"], row["destino"]]:
            if no not in contagem:
                contagem[no] = {t: 0 for t in TIPOS}
            contagem[no][row["tipo_conexao"]] += 1

    df_cont = (
        pd.DataFrame(contagem).T.reset_index()
        .rename(columns={"index": "aeroporto"})
        .merge(df_ego[["aeroporto", "regiao", "grau"]], on="aeroporto")
        .sort_values("grau", ascending=False)
    )
    for t in TIPOS:
        if t not in df_cont.columns:
            df_cont[t] = 0

    fig = go.Figure()
    for tipo in TIPOS:
        label = tipo.replace("_", " ").capitalize()
        fig.add_trace(go.Bar(
            x=df_cont["aeroporto"],
            y=df_cont[tipo].fillna(0),
            name=label,
            marker_color=CORES_TIPO[tipo],
            customdata=df_cont["regiao"],
            hovertemplate=f"<b>%{{x}}</b><br>{label}: %{{y}}<br>Regiao: %{{customdata}}<extra></extra>",
        ))

    fig.update_layout(**LAYOUT_BASE, barmode="stack", height=520,
                      title=dict(
                          text=("Exploratorio 2 - Composicao das Conexoes por Tipo"),
                          x=0.5, xanchor="center"),
                      xaxis=dict(title="Aeroporto", tickangle=-45,
                                 gridcolor="rgba(148,163,184,0.1)"),
                      yaxis=dict(title="No. de conexoes",
                                 gridcolor="rgba(148,163,184,0.1)"))

    _salvar_html(fig, os.path.join(pasta, "q10_exp2_composicao_conexoes.html"), "Exploratorio 2")


def _expl1_ranking_hubs(df_ego, pasta):
    df_sorted = df_ego.sort_values("grau", ascending=True)
    colors = [CORES[r] for r in df_sorted["regiao"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_sorted["grau"], y=df_sorted["aeroporto"],
        orientation="h",
        marker=dict(color=colors, line=dict(color="#07111f", width=0.5)),
        customdata=df_sorted[["regiao", "densidade_ego"]].values,
        hovertemplate=("<b>%{y}</b><br>Grau: %{x} conexoes<br>"
                       "Regiao: %{customdata[0]}<br>"
                       "Densidade ego: %{customdata[1]:.3f}<extra></extra>"),
        text=df_sorted["grau"].astype(int),
        textposition="outside",
        textfont=dict(color="#e5eefc", size=11),
        name="Grau",
    ))

    media = df_ego["grau"].mean()
    fig.add_vline(x=media, line=dict(color="#94a3b8", dash="dash", width=1.5),
                  annotation_text=f"Media: {media:.1f}",
                  annotation_font=dict(color="#94a3b8"))

    for regiao, cor in CORES.items():
        fig.add_trace(go.Bar(x=[None], y=[None], name=regiao,
                             marker_color=cor, showlegend=True))

    fig.update_layout(**LAYOUT_BASE,
                      height=max(480, len(df_sorted) * 26), showlegend=True,
                      title=dict(
                          text=("Explanatorio 1 - Ranking de Hubs da Rede"),
                          x=0.5, xanchor="center"),
                      xaxis=dict(title="Grau (conexoes diretas)",
                                 gridcolor="rgba(148,163,184,0.1)"),
                      yaxis=dict(title="Aeroporto",
                                 gridcolor="rgba(148,163,184,0.1)"))

    _salvar_html(fig, os.path.join(pasta, "q10_expl1_ranking_hubs.html"), "Explanatorio 1")


def _expl2_comparacao_regioes(df_ego, regioes, pasta):
    df_r = pd.DataFrame(regioes)
    grau_medio = (df_ego.groupby("regiao")["grau"]
                  .mean().rename("grau_medio").reset_index())
    df_r = df_r.merge(grau_medio, on="regiao")

    metricas = [
        ("ordem",      "No. de aeroportos",  "Aeroportos"),
        ("tamanho",    "No. de arestas",      "Arestas internas"),
        ("grau_medio", "Grau medio",          "Grau medio"),
    ]

    fig = make_subplots(rows=1, cols=3,
                        subplot_titles=[m[2] for m in metricas],
                        horizontal_spacing=0.10)

    for idx, (col, ylabel, title) in enumerate(metricas, start=1):
        df_plot = df_r.sort_values(col, ascending=False)
        colors  = [CORES[r] for r in df_plot["regiao"]]
        labels  = [f"{v:.1f}" if col == "grau_medio" else str(int(v))
                   for v in df_plot[col]]
        fig.add_trace(go.Bar(
            x=df_plot["regiao"], y=df_plot[col],
            marker=dict(color=colors, line=dict(color="#07111f", width=0.5)),
            text=labels, textposition="outside",
            textfont=dict(color="#e5eefc", size=11),
            hovertemplate=f"<b>%{{x}}</b><br>{ylabel}: %{{y}}<extra></extra>",
            showlegend=False,
        ), row=1, col=idx)
        fig.update_xaxes(tickangle=-22, gridcolor="rgba(148,163,184,0.1)", row=1, col=idx)
        fig.update_yaxes(title_text=ylabel, gridcolor="rgba(148,163,184,0.1)", row=1, col=idx)

    fig.update_layout(**LAYOUT_BASE, height=500, showlegend=False,
                      title=dict(
                          text=("Explanatorio 2 - Comparacao entre Regioes"),
                          x=0.5, xanchor="center"))

    _salvar_html(fig, os.path.join(pasta, "q10_expl2_comparacao_regioes.html"), "Explanatorio 2")


def _relatorio(df_ego, glob, regioes):
    sep = "=" * 58
    print(f"\n[Q10] {sep}")
    print("[Q10]  ANALISE EXPLORATORIA E EXPLANATORIA -- Q10")
    print(f"[Q10] {sep}")
    print(f"[Q10] Ordem={glob['ordem']}, Tamanho={glob['tamanho']}, Densidade={glob['densidade']:.4f}")
    print(f"[Q10] Grau medio={df_ego['grau'].mean():.2f}, max={df_ego['grau'].max()}, min={df_ego['grau'].min()}")
    media = df_ego["grau"].mean()
    std   = df_ego["grau"].std()
    hubs  = df_ego[df_ego["grau"] >= media + std].sort_values("grau", ascending=False)
    print(f"[Q10] Hubs (grau >= {media+std:.1f}):")
    for _, h in hubs.iterrows():
        print(f"  {h['aeroporto']} ({h['regiao']}) grau={h['grau']}")
    print(f"[Q10] {sep}\n")


def analise_avd(pasta_saida="out", pasta_data="data"):
    """Executa a analise AVD do Q10 e salva 4 visualizacoes interativas."""
    os.makedirs(pasta_saida, exist_ok=True)
    df_ego, _, df_adj, glob, regioes = _carregar(pasta_saida, pasta_data)
    _relatorio(df_ego, glob, regioes)
    _exp1_distribuicao(df_ego, pasta_saida)
    _exp2_composicao_conexoes(df_ego, df_adj, pasta_saida)
    _expl1_ranking_hubs(df_ego, pasta_saida)
    _expl2_comparacao_regioes(df_ego, regioes, pasta_saida)
    print("[Q10] 4 visualizacoes interativas geradas em out/\n")