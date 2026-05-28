"""
Gera out/dashboard.html -- dashboard unificado, visual premium.
"""
import json, os, sys
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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

# Apenas keys verdadeiramente globais -- sem xaxis/yaxis/margin/legend
# (esses variam por grafico e sao passados individualmente)
_L = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(7,17,31,0.55)",
    font=dict(family="Inter,'Segoe UI',Arial,sans-serif", color="#cbd5e1", size=12),
    hoverlabel=dict(
        bgcolor="#0f172a", bordercolor="rgba(99,179,237,0.5)",
        font=dict(color="#e5eefc", size=13),
        namelength=-1,
    ),
)

_LEGEND_H = dict(bgcolor="rgba(15,23,42,0.9)", bordercolor="rgba(148,163,184,0.2)",
                 borderwidth=1, font=dict(size=11), orientation="h",
                 yanchor="bottom", y=1.02, xanchor="right", x=1)
_LEGEND_V = dict(bgcolor="rgba(15,23,42,0.9)", bordercolor="rgba(148,163,184,0.2)",
                 borderwidth=1, font=dict(size=11), orientation="v",
                 x=1.01, xanchor="left", y=0.5, yanchor="middle")
_GRID = "rgba(148,163,184,0.08)"
_LINE = "rgba(148,163,184,0.1)"

def _ax():
    return dict(gridcolor=_GRID, zerolinecolor=_LINE, linecolor=_LINE, tickfont=dict(size=11))

def _div(fig):
    return fig.to_html(
        full_html=False, include_plotlyjs=False,
        config={"displayModeBar": True, "scrollZoom": True, "responsive": True,
                "modeBarButtonsToRemove": ["toImage"], "displaylogo": False},
    )

# ──────────────────────────────────────────────
# Chart builders
# ──────────────────────────────────────────────

def _c1_graus(df):
    """Histograma + boxplot por regiao."""
    regs = (df.groupby("regiao")["grau"].median()
              .sort_values(ascending=False).index.tolist())
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Distribuicao dos graus", "Grau por regiao"),
                        horizontal_spacing=0.14)

    # Histograma com gradiente
    grau_vals = sorted(df["grau"].unique())
    bar_colors = [f"rgba(71,123,157,{0.55 + 0.45*(v/max(grau_vals))})" for v in grau_vals]
    counts = [int((df["grau"] == g).sum()) for g in grau_vals]
    fig.add_trace(go.Bar(
        x=grau_vals, y=counts, name="Aeroportos",
        marker=dict(color=bar_colors, line=dict(color="rgba(7,17,31,0.6)", width=1)),
        hovertemplate="Grau <b>%{x}</b>: %{y} aeroportos<extra></extra>",
    ), row=1, col=1)

    media = df["grau"].mean()
    fig.add_vline(x=media, row=1, col=1,
                  line=dict(color="#E63946", dash="dash", width=1.8),
                  annotation_text=f"  Media {media:.1f}",
                  annotation_font=dict(color="#E63946", size=11))

    def hex_rgba(h, a):
        r,g,b = int(h[1:3],16), int(h[3:5],16), int(h[5:7],16)
        return f"rgba({r},{g},{b},{a})"

    # Boxplots coloridos
    for reg in regs:
        fig.add_trace(go.Box(
            y=df[df["regiao"] == reg]["grau"],
            name=reg, marker_color=CORES[reg], line_color=CORES[reg],
            boxmean="sd", fillcolor=hex_rgba(CORES[reg], 0.18),
            hovertemplate=f"<b>{reg}</b><br>Grau: %{{y}}<extra></extra>",
        ), row=1, col=2)

    fig.update_layout(**_L, height=370, showlegend=True, legend=_LEGEND_H,
                      margin=dict(t=24, b=48, l=52, r=20))
    for c,xt,yt in [(1,"Grau","Aeroportos"),(2,"Regiao","Grau")]:
        fig.update_xaxes(title_text=xt, **_ax(), row=1, col=c)
        fig.update_yaxes(title_text=yt, **_ax(), row=1, col=c)
    return _div(fig)


def _c2_composicao(df, df_adj):
    """Barras empilhadas por tipo de conexao."""
    TIPOS = ["regional", "regional_hub", "hub_nacional"]
    cont = {}
    for _, row in df_adj.iterrows():
        for no in [row["origem"], row["destino"]]:
            if no not in cont:
                cont[no] = {t: 0 for t in TIPOS}
            cont[no][row["tipo_conexao"]] += 1
    df_c = (
        pd.DataFrame(cont).T.reset_index()
        .rename(columns={"index": "aeroporto"})
        .merge(df[["aeroporto","regiao","grau"]], on="aeroporto")
        .sort_values("grau", ascending=False)
    )
    for t in TIPOS:
        if t not in df_c.columns:
            df_c[t] = 0

    fig = go.Figure()
    nomes = {"regional": "Regional", "regional_hub": "Hub regional", "hub_nacional": "Hub nacional"}
    for tipo in TIPOS:
        fig.add_trace(go.Bar(
            x=df_c["aeroporto"], y=df_c[tipo].fillna(0),
            name=nomes[tipo],
            marker=dict(color=CORES_TIPO[tipo],
                        line=dict(color="rgba(7,17,31,0.5)", width=0.5)),
            customdata=df_c["regiao"],
            hovertemplate=(
                "<b>%{x}</b><br>"
                f"{nomes[tipo]}: %{{y}}<br>"
                "Regiao: %{customdata}<extra></extra>"
            ),
        ))
    fig.update_layout(**_L, barmode="stack", height=370, showlegend=True,
                      legend=_LEGEND_H, margin=dict(t=24, b=56, l=52, r=20),
                      xaxis=dict(title="Aeroporto", tickangle=-50, **_ax()),
                      yaxis=dict(title="Conexoes", **_ax()))
    return _div(fig)


def _c3_hubs(df):
    """Ranking horizontal de hubs."""
    df_s = df.sort_values("grau", ascending=True)
    max_g = df_s["grau"].max()
    alphas = [0.5 + 0.5*(g/max_g) for g in df_s["grau"]]
    def hex_alpha(hex_c, a):
        r,g,b = int(hex_c[1:3],16),int(hex_c[3:5],16),int(hex_c[5:7],16)
        return f"rgba({r},{g},{b},{a:.2f})"
    colors = [hex_alpha(CORES[r], a) for r,a in zip(df_s["regiao"], alphas)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_s["grau"], y=df_s["aeroporto"], orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(7,17,31,0.5)", width=0.4)),
        customdata=df_s[["regiao","densidade_ego"]].values,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Grau: <b>%{x}</b> conexoes<br>"
            "Regiao: %{customdata[0]}<br>"
            "Dens. ego: %{customdata[1]:.3f}<extra></extra>"
        ),
        text=df_s["grau"].astype(int),
        textposition="outside",
        textfont=dict(color="#cbd5e1", size=11),
    ))
    media = df["grau"].mean()
    fig.add_vline(x=media, line=dict(color="#64748b", dash="dot", width=1.5),
                  annotation_text=f"  Media {media:.1f}",
                  annotation_font=dict(color="#64748b", size=11))
    for reg, cor in CORES.items():
        fig.add_trace(go.Bar(x=[None], y=[None], name=reg,
                             marker_color=cor, showlegend=True))
    fig.update_layout(**_L, height=max(370, len(df_s)*26), showlegend=True,
                      legend=_LEGEND_V, margin=dict(t=24, b=48, l=52, r=120),
                      xaxis=dict(title="Grau (conexoes diretas)", **_ax()),
                      yaxis=dict(**_ax()))
    return _div(fig)


def _c4_regioes(df, regioes):
    """Painel 3-em-1: aeroportos, arestas, grau medio."""
    df_r = pd.DataFrame(regioes)
    gm = df.groupby("regiao")["grau"].mean().rename("grau_medio").reset_index()
    df_r = df_r.merge(gm, on="regiao")
    mets = [("ordem","Aeroportos"),("tamanho","Arestas internas"),("grau_medio","Grau medio")]

    fig = make_subplots(rows=1, cols=3,
                        subplot_titles=[m[1] for m in mets],
                        horizontal_spacing=0.09)
    for idx,(col,lbl) in enumerate(mets,1):
        df_p = df_r.sort_values(col, ascending=False)
        colors = [CORES[r] for r in df_p["regiao"]]
        texts  = [f"{v:.1f}" if col=="grau_medio" else str(int(v)) for v in df_p[col]]
        fig.add_trace(go.Bar(
            x=df_p["regiao"], y=df_p[col],
            marker=dict(color=colors, line=dict(color="rgba(7,17,31,0.5)", width=0.5)),
            text=texts, textposition="outside",
            textfont=dict(color="#cbd5e1", size=11),
            hovertemplate=f"<b>%{{x}}</b><br>{lbl}: %{{y}}<extra></extra>",
            showlegend=False,
        ), row=1, col=idx)
        fig.update_xaxes(tickangle=-22, **_ax(), row=1, col=idx)
        fig.update_yaxes(title_text=lbl, **_ax(), row=1, col=idx)

    fig.update_layout(**_L, height=370, showlegend=False,
                      margin=dict(t=24, b=52, l=52, r=20))
    return _div(fig)


# ──────────────────────────────────────────────
# HTML generator
# ──────────────────────────────────────────────

def gerar_dashboard(pasta_saida="out", pasta_data="data"):
    df_ego  = pd.read_csv(os.path.join(pasta_saida,"ego_aeroportos.csv"))
    df_aero = pd.read_csv(os.path.join(pasta_data, "aeroportos_data.csv"))
    df_adj  = pd.read_csv(os.path.join(pasta_data, "adjacencias_aeroportos.csv"))
    with open(os.path.join(pasta_saida,"global.json"),  encoding="utf-8") as f: glob    = json.load(f)
    with open(os.path.join(pasta_saida,"regioes.json"), encoding="utf-8") as f: regioes = json.load(f)
    df_ego = (df_ego
        .merge(df_aero[["iata","regiao"]], left_on="aeroporto", right_on="iata", how="left")
        .drop(columns="iata"))

    d1 = _c1_graus(df_ego)
    d2 = _c2_composicao(df_ego, df_adj)
    d3 = _c3_hubs(df_ego)
    d4 = _c4_regioes(df_ego, regioes)

    hub      = df_ego.loc[df_ego["grau"].idxmax(), "aeroporto"]
    hub_grau = int(df_ego["grau"].max())
    n_aero   = glob["ordem"]
    n_con    = glob["tamanho"]
    n_reg    = len(regioes)
    dens     = glob["densidade"]

    # Badges por regiao para legenda visual
    badges = "".join(
        f'<span class="badge" style="--c:{c}">{r}</span>'
        for r,c in CORES.items()
    )

    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Dashboard - Rede de Aeroportos do Brasil</title>
  <script src="https://cdn.plot.ly/plotly-latest.min.js" charset="utf-8"></script>
  <style>
    /* ── RESET & TOKENS ── */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --bg0: #020617;
      --bg1: #07111f;
      --bg2: #0f172a;
      --panel: rgba(15,23,42,.82);
      --border: rgba(148,163,184,.18);
      --border-hi: rgba(99,179,237,.35);
      --text: #e5eefc;
      --muted: #94a3b8;
      --blue: #3b82f6;
      --red: #ff4d6d;
      --teal: #2dd4bf;
      --amber: #fbbf24;
      --radius-xl: 22px;
      --radius-lg: 16px;
      --shadow-lg: 0 24px 60px rgba(0,0,0,.38);
      --shadow-md: 0 12px 36px rgba(0,0,0,.28);
      --blur: blur(18px);
    }}
    html {{ scroll-behavior: smooth; }}
    body {{
      font-family: Inter, "Segoe UI", Arial, sans-serif;
      color: var(--text);
      background:
        radial-gradient(ellipse 80% 50% at 10% 0%, rgba(59,130,246,.18), transparent),
        radial-gradient(ellipse 60% 40% at 90% 5%,  rgba(255,77,109,.16), transparent),
        radial-gradient(ellipse 50% 60% at 50% 100%, rgba(45,212,191,.08), transparent),
        linear-gradient(160deg, var(--bg0) 0%, var(--bg1) 50%, var(--bg2) 100%);
      min-height: 100vh;
    }}

    /* ── HERO ── */
    .hero {{
      max-width: 1240px; margin: 0 auto;
      padding: 56px 32px 40px;
    }}
    .hero-eyebrow {{
      display: inline-flex; align-items: center; gap: 8px;
      background: rgba(59,130,246,.12); border: 1px solid rgba(59,130,246,.3);
      color: #93c5fd; border-radius: 999px;
      font-size: 12px; font-weight: 700; letter-spacing: .08em;
      text-transform: uppercase; padding: 5px 14px; margin-bottom: 18px;
    }}
    .hero h1 {{
      font-size: clamp(32px, 5vw, 58px);
      font-weight: 900; letter-spacing: -.05em; line-height: 1.05;
      background: linear-gradient(135deg, #f0f9ff 30%, #93c5fd 70%, #818cf8 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text;
    }}
    .hero p {{
      color: var(--muted); margin-top: 12px; font-size: 16px;
      max-width: 600px; line-height: 1.6;
    }}
    .region-badges {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 20px; }}
    .badge {{
      padding: 5px 12px; border-radius: 999px; font-size: 11px; font-weight: 700;
      background: rgba(var(--c), .15);
      border: 1px solid color-mix(in srgb, var(--c) 60%, transparent);
      color: var(--c);
    }}

    /* ── METRICS ── */
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px,1fr));
      gap: 14px; margin-top: 32px;
    }}
    .mc {{
      position: relative; overflow: hidden;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 20px 22px;
      backdrop-filter: var(--blur);
      box-shadow: var(--shadow-md);
      transition: transform .2s, box-shadow .2s, border-color .2s;
    }}
    .mc:hover {{
      transform: translateY(-3px);
      box-shadow: var(--shadow-lg);
      border-color: var(--border-hi);
    }}
    .mc::before {{
      content: "";
      position: absolute; inset: 0 0 auto 0; height: 2px;
      background: linear-gradient(90deg, var(--ac, var(--blue)), transparent);
    }}
    .mc .ico {{ font-size: 22px; margin-bottom: 10px; display: block; }}
    .mc .v {{
      font-size: 32px; font-weight: 900; letter-spacing: -.04em;
      color: var(--ac, #f0f9ff); line-height: 1;
    }}
    .mc .l {{
      font-size: 11px; color: var(--muted); margin-top: 6px;
      font-weight: 700; text-transform: uppercase; letter-spacing: .07em;
    }}

    /* ── TABS ── */
    .tabs-wrap {{ max-width: 1240px; margin: 0 auto; padding: 0 32px 72px; }}
    .tabs-nav {{
      display: flex; gap: 2px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 32px;
    }}
    .tb {{
      position: relative;
      border: none; background: none; cursor: pointer;
      color: var(--muted);
      font: 700 14px/1 Inter, sans-serif;
      padding: 12px 24px 15px;
      border-radius: 10px 10px 0 0;
      margin-bottom: -1px;
      transition: color .18s, background .18s;
    }}
    .tb::after {{
      content: ""; position: absolute; bottom: -1px; left: 0; right: 0;
      height: 3px; border-radius: 3px 3px 0 0;
      background: var(--blue); transform: scaleX(0);
      transition: transform .22s cubic-bezier(.4,0,.2,1);
    }}
    .tb:hover {{ color: var(--text); background: rgba(255,255,255,.04); }}
    .tb.on {{ color: var(--text); }}
    .tb.on::after {{ transform: scaleX(1); }}
    .pane {{ display: none; animation: fadeUp .28s ease; }}
    .pane.on {{ display: block; }}
    @keyframes fadeUp {{
      from {{ opacity: 0; transform: translateY(10px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}

    /* ── SECTION HEAD ── */
    .sh {{ margin-bottom: 24px; }}
    .sh h2 {{
      font-size: 22px; font-weight: 800; letter-spacing: -.03em;
      color: #f0f9ff;
    }}
    .sh p {{ color: var(--muted); font-size: 13px; margin-top: 5px; line-height: 1.5; }}

    /* ── CARDS ── */
    .card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius-xl);
      overflow: hidden;
      backdrop-filter: var(--blur);
      box-shadow: var(--shadow-md);
      transition: border-color .2s, box-shadow .2s;
    }}
    .card:hover {{
      border-color: rgba(148,163,184,.32);
      box-shadow: var(--shadow-lg);
    }}
    .card-hd {{
      padding: 20px 24px 16px;
      border-bottom: 1px solid var(--border);
      display: flex; align-items: flex-start; gap: 12px;
    }}
    .card-hd-ico {{
      font-size: 24px; flex-shrink: 0; margin-top: 2px;
    }}
    .card-hd h3 {{
      font-size: 15px; font-weight: 800; color: #f0f9ff; line-height: 1.3;
    }}
    .card-hd .sub {{
      font-size: 12px; color: var(--muted); margin-top: 3px; line-height: 1.4;
    }}
    .card-bd {{ padding: 4px 2px 2px; }}

    .grid2 {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(460px,1fr));
      gap: 20px; margin-bottom: 20px;
    }}

    /* ── IFRAME ── */
    .iframe-wrap {{
      border: 1px solid var(--border);
      border-radius: var(--radius-xl);
      overflow: hidden;
      box-shadow: var(--shadow-lg);
      transition: border-color .2s;
    }}
    .iframe-wrap:hover {{ border-color: rgba(148,163,184,.32); }}
    .iframe-wrap iframe {{
      width: 100%; border: none; display: block;
    }}

    /* ── FOOTER ── */
    .footer {{
      max-width: 1240px; margin: 0 auto;
      padding: 0 32px 40px;
      color: var(--muted); font-size: 12px;
      display: flex; justify-content: space-between; align-items: center;
      flex-wrap: wrap; gap: 8px;
      border-top: 1px solid var(--border); padding-top: 24px; margin-top: -40px;
    }}
    .footer span {{ opacity: .7; }}
  </style>
</head>
<body>

<!-- ── HERO ── -->
<div class="hero">
  <div class="hero-eyebrow">Teoria dos Grafos &mdash; Analise da Malha Aerea</div>
  <h1>Rede de Aeroportos<br>do Brasil</h1>
  <p>Analise exploratoria e explanatoria de {n_aero} aeroportos e {n_con} conexoes organizados em {n_reg} regioes.</p>
  <div class="region-badges">{badges}</div>
  <div class="metrics">
    <div class="mc" style="--ac:#3b82f6">
      <span class="ico">✈️</span>
      <div class="v">{n_aero}</div>
      <div class="l">Aeroportos</div>
    </div>
    <div class="mc" style="--ac:#2dd4bf">
      <span class="ico">🔗</span>
      <div class="v">{n_con}</div>
      <div class="l">Conexoes</div>
    </div>
    <div class="mc" style="--ac:#ff4d6d">
      <span class="ico">🗺️</span>
      <div class="v">{n_reg}</div>
      <div class="l">Regioes</div>
    </div>
    <div class="mc" style="--ac:#fbbf24">
      <span class="ico">📊</span>
      <div class="v">{dens:.4f}</div>
      <div class="l">Densidade global</div>
    </div>
    <div class="mc" style="--ac:#a78bfa">
      <span class="ico">🏆</span>
      <div class="v">{hub}</div>
      <div class="l">Hub principal &bull; {hub_grau} conexoes</div>
    </div>
  </div>
</div>

<!-- ── TABS ── -->
<div class="tabs-wrap">
  <nav class="tabs-nav">
    <button class="tb on"  onclick="tab('analise',this)">📊&nbsp; Analise Q10</button>
    <button class="tb"     onclick="tab('percursos',this)">🛤️&nbsp; Percursos</button>
    <button class="tb"     onclick="tab('rede',this)">🌐&nbsp; Grafo da Rede</button>
  </nav>

  <!-- ABA ANALISE -->
  <div class="pane on" id="p-analise">
    <div class="sh">
      <h2>Analise Exploratoria e Explanatoria</h2>
      <p>Passe o mouse para detalhes &bull; Scroll ou arraste para zoom &bull; Clique na legenda para filtrar series</p>
    </div>

    <div class="grid2">
      <div class="card">
        <div class="card-hd">
          <div class="card-hd-ico">📈</div>
          <div>
            <h3>Exploratorio 1 &mdash; Distribuicao dos Graus</h3>
            <div class="sub">Histograma de graus + boxplot por regiao</div>
          </div>
        </div>
        <div class="card-bd">{d1}</div>
      </div>
      <div class="card">
        <div class="card-hd">
          <div class="card-hd-ico">📊</div>
          <div>
            <h3>Exploratorio 2 &mdash; Composicao das Conexoes</h3>
            <div class="sub">Tipos de conexao em cada aeroporto (barras empilhadas)</div>
          </div>
        </div>
        <div class="card-bd">{d2}</div>
      </div>
    </div>

    <div class="card" style="margin-bottom:20px">
      <div class="card-hd">
        <div class="card-hd-ico">🏆</div>
        <div>
          <h3>Explanatorio 1 &mdash; Ranking de Hubs</h3>
          <div class="sub">Aeroportos ordenados pelo numero de conexoes diretas, coloridos por regiao</div>
        </div>
      </div>
      <div class="card-bd">{d3}</div>
    </div>

    <div class="card">
      <div class="card-hd">
        <div class="card-hd-ico">🗺️</div>
        <div>
          <h3>Explanatorio 2 &mdash; Comparacao entre Regioes</h3>
          <div class="sub">Volume de aeroportos, arestas internas e grau medio por regiao</div>
        </div>
      </div>
      <div class="card-bd">{d4}</div>
    </div>
  </div>

  <!-- ABA PERCURSOS -->
  <div class="pane" id="p-percursos">
    <div class="sh">
      <h2>Percursos Obrigatorios</h2>
      <p>Subgrafo com os caminhos de menor custo (Dijkstra). Arraste nos, faca pan e use scroll para zoom.</p>
    </div>
    <div class="iframe-wrap">
      <iframe src="arvore_percurso.html" height="760"></iframe>
    </div>
  </div>

  <!-- ABA REDE -->
  <div class="pane" id="p-rede">
    <div class="sh">
      <h2>Grafo Completo da Rede</h2>
      <p>Simulacao de fisica interativa. Nos coloridos por regiao, arestas por tipo de conexao.</p>
    </div>
    <div class="iframe-wrap">
      <iframe src="grafo_interativo.html" height="780"></iframe>
    </div>
  </div>
</div>

<!-- FOOTER -->
<footer class="footer">
  <span>Teoria dos Grafos &mdash; Rede de Aeroportos do Brasil</span>
  <span>Plotly &bull; PyVis &bull; SVG/JS &bull; Python</span>
</footer>

<script>
  function tab(name, btn) {{
    document.querySelectorAll('.pane').forEach(p => p.classList.remove('on'));
    document.querySelectorAll('.tb').forEach(b => b.classList.remove('on'));
    document.getElementById('p-' + name).classList.add('on');
    btn.classList.add('on');
    setTimeout(() => window.dispatchEvent(new Event('resize')), 60);
  }}
</script>
</body>
</html>"""

    caminho = os.path.join(pasta_saida, "dashboard.html")
    with open(caminho, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"[DASH] dashboard.html gerado -> {caminho}")
    return caminho


if __name__ == "__main__":
    gerar_dashboard()