from __future__ import annotations

import html
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graphs.io import carregar_grafo
from graphs.algorithms import dijkstra

# ──────────────────────────────────────────────────────────────────────────
# PALETA CANÔNICA — fonte única de cores das visualizações.
# Espelhada em dashboard/src/constants.jsx (front React) para garantir
# conformidade visual entre o front e as saídas estáticas em out/.
# ──────────────────────────────────────────────────────────────────────────
CORES = {
    "Nordeste":     "#E63946",
    "Sudeste":      "#457B9D",
    "Sul":          "#2A9D8F",
    "Norte":        "#E9C46A",
    "Centro-Oeste": "#F4A261",
}

# Cores por tipo de conexão (modelo de arestas do grupo)
CORES_TIPO = {
    "regional":     "#A8DADC",
    "regional_hub": "#457B9D",
    "hub_nacional": "#E63946",
}

# Cores cíclicas para destacar cada percurso obrigatório
ROTA_CORES = ["#3b82f6", "#ff4d6d", "#2dd4bf", "#fbbf24",
              "#a78bfa", "#f97316", "#34d399", "#f472b6"]

ROTAS_OBRIGATORIAS = [
    ("REC", "POA"),  
    ("MAO", "CGH"),  
]

def construir_subgrafo_percursos(grafo, rotas: list[tuple[str, str]]):
    caminhos = []
    arestas = set()
    nos = set()

    for origem, destino in rotas:
        origem = origem.strip().upper()
        destino = destino.strip().upper()

        if origem not in grafo.adj:
            raise ValueError(f"Aeroporto de origem não encontrado no grafo: {origem}")
        if destino not in grafo.adj:
            raise ValueError(f"Aeroporto de destino não encontrado no grafo: {destino}")

        custo, caminho = dijkstra(grafo, origem, destino)

        if not caminho:
            raise ValueError(f"Não existe caminho entre {origem} e {destino}.")

        caminhos.append({
            "origem": origem,
            "destino": destino,
            "custo": custo,
            "caminho": caminho,
        })

        nos.update(caminho)

        for i in range(len(caminho) - 1):
            u, v = caminho[i], caminho[i + 1]
            arestas.add(tuple(sorted((u, v))))

    return nos, arestas, caminhos


def _rotulo_aeroporto(grafo, iata: str) -> str:
    info = grafo.nodes_info.get(iata, {})
    cidade = info.get("cidade", "")
    return f"{iata} - {cidade}" if cidade else iata


def _posicoes_por_caminho(caminhos: list[dict]) -> dict[str, tuple[int, int]]:
    posicoes = {}
    espacamento_x = 230
    espacamento_y = 210
    margem_x = 130
    margem_y = 135

    for linha, item in enumerate(caminhos):
        caminho = item["caminho"]
        y = margem_y + linha * espacamento_y

        for coluna, no in enumerate(caminho):
            x = margem_x + coluna * espacamento_x

            if no in posicoes:
                x_antigo, y_antigo = posicoes[no]
                posicoes[no] = (x_antigo, int((y_antigo + y) / 2))
            else:
                posicoes[no] = (x, y)

    return posicoes


_ESTILO_BASE = """
    *{box-sizing:border-box;margin:0}
    body{background:#fff;overflow:hidden}
    #wrap{width:100vw;height:100vh;cursor:grab}
    #wrap:active{cursor:grabbing}
    svg{width:100%;height:100%;display:block}
    .edge{stroke-linecap:round;transition:stroke-width .15s}
    .node{cursor:move}
    .node circle{stroke:#fff;stroke-width:2.5;filter:drop-shadow(0 4px 8px rgba(0,0,0,.15));transition:filter .15s}
    .node:hover circle{filter:drop-shadow(0 0 10px rgba(59,130,246,.5))}
    .iata{fill:#fff;font-family:system-ui,sans-serif;font-size:14px;font-weight:900;text-anchor:middle;dominant-baseline:middle;pointer-events:none}
    .city{fill:#475569;font-family:system-ui,sans-serif;font-size:12px;font-weight:600;text-anchor:middle;pointer-events:none}
    .edge-label{fill:#64748b;font-family:system-ui,sans-serif;font-size:11px;font-weight:700;text-anchor:middle}
    .level-label{fill:#94a3b8;font-family:system-ui,sans-serif;font-size:12px;font-weight:700;text-anchor:middle}
    .tooltip{position:fixed;pointer-events:none;opacity:0;transform:translateY(4px);background:#1e293b;color:#f1f5f9;
      border-radius:10px;padding:8px 12px;font-size:13px;font-family:system-ui,sans-serif;
      box-shadow:0 8px 24px rgba(0,0,0,.18);transition:opacity .12s,transform .12s;z-index:20}
    .tooltip.visible{opacity:1;transform:translateY(0)}
    .tooltip strong{display:block;margin-bottom:3px}
    .tooltip span{color:#94a3b8;display:block}"""

_JS_INTERACAO = """
    const svg=document.getElementById('graph'),viewport=document.getElementById('viewport'),tooltip=document.getElementById('tooltip');
    let scale=1,translateX=0,translateY=0,selectedNode=null,isPanning=false,panStart={x:0,y:0,tx:0,ty:0};
    function nodeById(id){return nodes.find(n=>n.id===id);}
    function updateTransform(){viewport.setAttribute('transform',`translate(${translateX},${translateY}) scale(${scale})`);}
    function svgPoint(e){
      const pt=svg.createSVGPoint();pt.x=e.clientX;pt.y=e.clientY;
      const c=pt.matrixTransform(svg.getScreenCTM().inverse());
      return {x:(c.x-translateX)/scale,y:(c.y-translateY)/scale};
    }
    function moveTooltip(e){tooltip.style.left=`${e.clientX+14}px`;tooltip.style.top=`${e.clientY+14}px`;}
    function hideTooltip(){tooltip.classList.remove('visible');}
    svg.addEventListener('mousedown',e=>{
      if(e.target.closest&&e.target.closest('.node')) return;
      isPanning=true;panStart={x:e.clientX,y:e.clientY,tx:translateX,ty:translateY};
    });
    window.addEventListener('mousemove',e=>{
      if(selectedNode){const p=svgPoint(e);selectedNode.x=p.x;selectedNode.y=p.y;updatePositions();moveTooltip(e);}
      else if(isPanning){translateX=panStart.tx+(e.clientX-panStart.x)/1.8;translateY=panStart.ty+(e.clientY-panStart.y)/1.8;updateTransform();}
    });
    window.addEventListener('mouseup',()=>{selectedNode=null;isPanning=false;});
    svg.addEventListener('wheel',e=>{
      e.preventDefault();scale=Math.min(2.6,Math.max(0.45,scale*(e.deltaY<0?1.1:0.9)));updateTransform();
    });"""


def exportar_arvore_percurso(
    caminho_aeroportos: str = "data/aeroportos_data.csv",
    caminho_adjacencias: str = "data/adjacencias_aeroportos.csv",
    pasta_saida: str = "out",
    arquivo_saida: str = "arvore_percurso.html",
    rotas: list[tuple[str, str]] | None = None,
) -> str:
    rotas = rotas or ROTAS_OBRIGATORIAS

    os.makedirs(pasta_saida, exist_ok=True)

    grafo, _ = carregar_grafo(caminho_aeroportos, caminho_adjacencias)

    nos, arestas, caminhos = construir_subgrafo_percursos(grafo, rotas)
    posicoes = _posicoes_por_caminho(caminhos)

    cores = ["#ff4d6d", "#3b82f6", "#10b981", "#8b5cf6"]
    cor_por_aresta = {}
    rota_por_aresta = {}

    for indice, item in enumerate(caminhos):
        cor = cores[indice % len(cores)]
        caminho = item["caminho"]
        nome_rota = f'{item["origem"]} → {item["destino"]}'

        for i in range(len(caminho) - 1):
            aresta = tuple(sorted((caminho[i], caminho[i + 1])))
            cor_por_aresta[aresta] = cor
            rota_por_aresta[aresta] = nome_rota

    nodes_data = []
    for no in sorted(nos):
        x, y = posicoes[no]
        info = grafo.nodes_info.get(no, {})
        nodes_data.append({
            "id": no,
            "label": _rotulo_aeroporto(grafo, no),
            "cidade": info.get("cidade", ""),
            "regiao": info.get("regiao", ""),
            "x": x,
            "y": y,
        })

    edges_data = []
    for u, v in sorted(arestas):
        aresta = tuple(sorted((u, v)))
        edges_data.append({
            "source": u,
            "target": v,
            "weight": grafo.adj[u][v],
            "color": cor_por_aresta.get(aresta, "#64748b"),
            "route": rota_por_aresta.get(aresta, "Percurso obrigatório"),
        })

    largura = max(x for x, _ in posicoes.values()) + 170
    altura = max(y for _, y in posicoes.values()) + 145

    conteudo_html = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Árvore dos percursos obrigatórios</title>
  <style>{_ESTILO_BASE}</style>
</head>
<body>
  <div id="wrap"><svg id="graph" viewBox="0 0 {largura} {altura}"><g id="viewport"></g></svg></div>
  <div class="tooltip" id="tooltip"></div>
  <script>
    const nodes = {json.dumps(nodes_data, ensure_ascii=False)};
    const edges = {json.dumps(edges_data, ensure_ascii=False)};
    {_JS_INTERACAO}
    function render(){{
      viewport.innerHTML='';
      edges.forEach((edge,i)=>{{
        const s=nodeById(edge.source),t=nodeById(edge.target);
        const line=document.createElementNS('http://www.w3.org/2000/svg','line');
        line.setAttribute('class','edge');line.setAttribute('id',`edge-${{i}}`);
        line.setAttribute('x1',s.x);line.setAttribute('y1',s.y);
        line.setAttribute('x2',t.x);line.setAttribute('y2',t.y);
        line.setAttribute('stroke',edge.color);line.setAttribute('stroke-width',4);line.setAttribute('opacity','0.8');
        line.addEventListener('mouseenter',()=>line.setAttribute('stroke-width',7));
        line.addEventListener('mouseleave',()=>line.setAttribute('stroke-width',4));
        viewport.appendChild(line);
        const lbl=document.createElementNS('http://www.w3.org/2000/svg','text');
        lbl.setAttribute('class','edge-label');lbl.setAttribute('id',`edge-lbl-${{i}}`);
        lbl.setAttribute('x',(s.x+t.x)/2);lbl.setAttribute('y',(s.y+t.y)/2-10);
        lbl.textContent=`peso ${{edge.weight}}`;
        viewport.appendChild(lbl);
      }});
      nodes.forEach(node=>{{
        const g=document.createElementNS('http://www.w3.org/2000/svg','g');
        g.setAttribute('class','node');g.setAttribute('transform',`translate(${{node.x}},${{node.y}})`);g.dataset.id=node.id;
        const circle=document.createElementNS('http://www.w3.org/2000/svg','circle');
        circle.setAttribute('r',34);circle.setAttribute('fill','#334155');g.appendChild(circle);
        const iata=document.createElementNS('http://www.w3.org/2000/svg','text');
        iata.setAttribute('class','iata');iata.setAttribute('y',5);iata.textContent=node.id;g.appendChild(iata);
        const city=document.createElementNS('http://www.w3.org/2000/svg','text');
        city.setAttribute('class','city');city.setAttribute('y',56);city.textContent=node.label;g.appendChild(city);
        g.addEventListener('mousedown',e=>{{e.stopPropagation();selectedNode=node;}});
        g.addEventListener('mouseenter',e=>{{
          const deg=edges.filter(ed=>ed.source===node.id||ed.target===node.id).length;
          tooltip.innerHTML=`<strong>${{node.label}}</strong><span>Região: ${{node.regiao||'—'}}</span><span>Conexões: ${{deg}}</span>`;
          tooltip.classList.add('visible');moveTooltip(e);
        }});
        g.addEventListener('mousemove',moveTooltip);g.addEventListener('mouseleave',hideTooltip);
        viewport.appendChild(g);
      }});
      updateTransform();
    }}
    function updatePositions(){{
      nodes.forEach(node=>{{
        const g=viewport.querySelector(`.node[data-id="${{node.id}}"]`);
        if(g) g.setAttribute('transform',`translate(${{node.x}},${{node.y}})`);
      }});
      edges.forEach((edge,i)=>{{
        const s=nodeById(edge.source),t=nodeById(edge.target);
        const line=document.getElementById(`edge-${{i}}`);
        const lbl=document.getElementById(`edge-lbl-${{i}}`);
        line.setAttribute('x1',s.x);line.setAttribute('y1',s.y);
        line.setAttribute('x2',t.x);line.setAttribute('y2',t.y);
        lbl.setAttribute('x',(s.x+t.x)/2);lbl.setAttribute('y',(s.y+t.y)/2-10);
      }});
    }}
    render();
  </script>
</body>
</html>
"""

    caminho_saida = os.path.join(pasta_saida, arquivo_saida)
    with open(caminho_saida, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo_html)

    print(f"[Q7] {caminho_saida} gerado com sucesso.")
    return caminho_saida


def exportar_subgrafo_maior_grau(
    caminho_aeroportos="data/aeroportos_data.csv",
    caminho_adjacencias="data/adjacencias_aeroportos.csv",
    pasta_saida="out",
    arquivo_saida="subgrafo_maior_grau.html",
    top_n=10,
):
    os.makedirs(pasta_saida, exist_ok=True)
    grafo, _ = carregar_grafo(caminho_aeroportos, caminho_adjacencias)

    graus = {no: len(viz) for no, viz in grafo.adj.items()}
    top_nos = sorted(graus, key=graus.get, reverse=True)[:top_n]
    top_set = set(top_nos)

    cx, cy, raio_layout = 500, 380, 290
    n = len(top_nos)
    posicoes = {}
    for i, no in enumerate(top_nos):
        ang = 2 * math.pi * i / n - math.pi / 2
        posicoes[no] = (int(cx + raio_layout * math.cos(ang)), int(cy + raio_layout * math.sin(ang)))

    cores_regiao = {
        'Nordeste': '#f59e0b', 'Sudeste': '#3b82f6',
        'Sul': '#10b981', 'Centro-Oeste': '#8b5cf6', 'Norte': '#ef4444',
    }
    grau_min = min(graus[no] for no in top_nos)
    grau_max = max(graus[no] for no in top_nos)

    nodes_data = []
    for no in top_nos:
        x, y = posicoes[no]
        info = grafo.nodes_info.get(no, {})
        regiao = info.get("regiao", "")
        nodes_data.append({
            "id": no,
            "label": f"{no} – {info.get('cidade', '')}" if info.get('cidade') else no,
            "cidade": info.get("cidade", ""),
            "regiao": regiao,
            "grau": graus[no],
            "cor": cores_regiao.get(regiao, '#64748b'),
            "raio": 28 + int((graus[no] - grau_min) / max(grau_max - grau_min, 1) * 14),
            "x": x,
            "y": y,
        })

    edges_data = []
    seen: set = set()
    for u in top_nos:
        for v, peso in grafo.adj[u].items():
            if v in top_set:
                aresta = tuple(sorted((u, v)))
                if aresta not in seen:
                    seen.add(aresta)
                    edges_data.append({"source": u, "target": v, "weight": peso})

    largura, altura = cx * 2, cy * 2 + 40

    conteudo_html = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Subgrafo — {top_n} Aeroportos com Maior Grau</title>
  <style>{_ESTILO_BASE}</style>
</head>
<body>
  <div id="wrap"><svg id="graph" viewBox="0 0 {largura} {altura}"><g id="viewport"></g></svg></div>
  <div class="tooltip" id="tooltip"></div>
  <script>
    const nodes = {json.dumps(nodes_data, ensure_ascii=False)};
    const edges = {json.dumps(edges_data, ensure_ascii=False)};
    {_JS_INTERACAO}
    function render(){{
      viewport.innerHTML='';
      edges.forEach((edge,i)=>{{
        const s=nodeById(edge.source),t=nodeById(edge.target);
        const line=document.createElementNS('http://www.w3.org/2000/svg','line');
        line.setAttribute('class','edge');line.setAttribute('id',`edge-${{i}}`);
        line.setAttribute('x1',s.x);line.setAttribute('y1',s.y);
        line.setAttribute('x2',t.x);line.setAttribute('y2',t.y);
        const sw=edge.weight>=2?4:edge.weight>=1.5?3:2;
        line.setAttribute('stroke','#94a3b8');line.setAttribute('stroke-width',sw);line.setAttribute('opacity','0.7');
        line.addEventListener('mouseenter',()=>line.setAttribute('stroke-width',sw+2));
        line.addEventListener('mouseleave',()=>line.setAttribute('stroke-width',sw));
        viewport.appendChild(line);
      }});
      nodes.forEach(node=>{{
        const g=document.createElementNS('http://www.w3.org/2000/svg','g');
        g.setAttribute('class','node');g.setAttribute('transform',`translate(${{node.x}},${{node.y}})`);g.dataset.id=node.id;
        const circle=document.createElementNS('http://www.w3.org/2000/svg','circle');
        circle.setAttribute('r',node.raio);circle.setAttribute('fill',node.cor);g.appendChild(circle);
        const iata=document.createElementNS('http://www.w3.org/2000/svg','text');
        iata.setAttribute('class','iata');iata.setAttribute('y',5);
        iata.setAttribute('font-size',node.raio>38?'15':'13');
        iata.textContent=node.id;g.appendChild(iata);
        const city=document.createElementNS('http://www.w3.org/2000/svg','text');
        city.setAttribute('class','city');city.setAttribute('y',node.raio+18);
        city.textContent=node.label;g.appendChild(city);
        g.addEventListener('mousedown',e=>{{e.stopPropagation();selectedNode=node;}});
        g.addEventListener('mouseenter',e=>{{
          tooltip.innerHTML=`<strong>${{node.label}}</strong><span>Região: ${{node.regiao||'—'}}</span><span>Grau: ${{node.grau}}</span>`;
          tooltip.classList.add('visible');moveTooltip(e);
        }});
        g.addEventListener('mousemove',moveTooltip);g.addEventListener('mouseleave',hideTooltip);
        viewport.appendChild(g);
      }});
      updateTransform();
    }}
    function updatePositions(){{
      nodes.forEach(node=>{{
        const g=viewport.querySelector(`.node[data-id="${{node.id}}"]`);
        if(g) g.setAttribute('transform',`translate(${{node.x}},${{node.y}})`);
      }});
      edges.forEach((edge,i)=>{{
        const s=nodeById(edge.source),t=nodeById(edge.target);
        const line=document.getElementById(`edge-${{i}}`);
        line.setAttribute('x1',s.x);line.setAttribute('y1',s.y);
        line.setAttribute('x2',t.x);line.setAttribute('y2',t.y);
      }});
    }}
    render();
  </script>
</body>
</html>
"""

    caminho_saida = os.path.join(pasta_saida, arquivo_saida)
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(conteudo_html)

    print(f"[AVD] Subgrafo dos {top_n} aeroportos com maior grau salvo em: {caminho_saida}")
    return caminho_saida


def exportar_bfs_camadas(
    caminho_aeroportos="data/aeroportos_data.csv",
    caminho_adjacencias="data/adjacencias_aeroportos.csv",
    pasta_saida="out",
    arquivo_saida="bfs_camadas.html",
    origem="GRU",
):
    from graphs.algorithms import bfs as _bfs

    os.makedirs(pasta_saida, exist_ok=True)
    grafo, _ = carregar_grafo(caminho_aeroportos, caminho_adjacencias)

    if origem not in grafo.adj:
        raise ValueError(f"Aeroporto de origem não encontrado: {origem}")

    _, niveis, predecessores = _bfs(grafo, origem)

    niveis_agrupados: dict = {}
    for no, nivel in niveis.items():
        niveis_agrupados.setdefault(nivel, []).append(no)

    def _ordenar_por_pred(nivel, nos_nivel):
        if nivel == 0:
            return sorted(nos_nivel)
        grupos: dict = {}
        for no in nos_nivel:
            grupos.setdefault(predecessores.get(no), []).append(no)
        grupos_ord = sorted(grupos.items(), key=lambda kv: posicoes.get(kv[0], (0, 0))[0])
        return [no for _, nos in grupos_ord for no in sorted(nos)]

    espacamento_y = 160
    margem_x = 80
    margem_y = 80
    max_nos = max(len(nos) for nos in niveis_agrupados.values())
    total_width = max(max_nos * 110, 600)

    largura = margem_x + total_width + margem_x
    altura = margem_y + (len(niveis_agrupados) - 1) * espacamento_y + margem_y

    posicoes: dict = {}
    for nivel in sorted(niveis_agrupados.keys()):
        nos_ord = _ordenar_por_pred(nivel, niveis_agrupados[nivel])
        niveis_agrupados[nivel] = nos_ord
        y = margem_y + nivel * espacamento_y
        n = len(nos_ord)
        for j, no in enumerate(nos_ord):
            posicoes[no] = (int(margem_x + (j + 0.5) * (total_width / n)), y)

    cores_niveis = ['#f59e0b', '#3b82f6', '#10b981', '#8b5cf6', '#ef4444', '#06b6d4', '#f97316', '#a78bfa']

    nodes_data = []
    for no, nivel in sorted(niveis.items(), key=lambda kv: (kv[1], kv[0])):
        x, y = posicoes[no]
        info = grafo.nodes_info.get(no, {})
        nodes_data.append({
            "id": no,
            "label": f"{no} – {info.get('cidade', '')}" if info.get('cidade') else no,
            "cidade": info.get("cidade", ""),
            "regiao": info.get("regiao", ""),
            "nivel": nivel,
            "cor": cores_niveis[nivel % len(cores_niveis)],
            "x": x,
            "y": y,
        })

    edges_data = []
    for no, pred in predecessores.items():
        if pred is not None:
            nivel_alvo = niveis[no]
            edges_data.append({
                "source": pred,
                "target": no,
                "color": cores_niveis[nivel_alvo % len(cores_niveis)],
            })

    nivel_labels_js = json.dumps(
        {str(nivel): {"x": int(margem_x + (len(nos) / 2) * (total_width / len(nos))), "y": margem_y + nivel * espacamento_y}
         for nivel, nos in niveis_agrupados.items()}
    )

    conteudo_html = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>BFS — Camadas a partir de {html.escape(origem)}</title>
  <style>{_ESTILO_BASE}</style>
</head>
<body>
  <div id="wrap"><svg id="graph" viewBox="0 0 {largura} {altura}"><g id="viewport"></g></svg></div>
  <div class="tooltip" id="tooltip"></div>
  <script>
    const nodes = {json.dumps(nodes_data, ensure_ascii=False)};
    const edges = {json.dumps(edges_data, ensure_ascii=False)};
    const nivelInfo = {nivel_labels_js};
    {_JS_INTERACAO}
    function render(){{
      viewport.innerHTML='';
      Object.entries(nivelInfo).forEach(([nivel,pos])=>{{
        const lbl=document.createElementNS('http://www.w3.org/2000/svg','text');
        lbl.setAttribute('class','level-label');
        lbl.setAttribute('x',30);lbl.setAttribute('y',pos.y+5);
        lbl.textContent=nivel==='0'?'Origem':`Camada ${{nivel}}`;
        viewport.appendChild(lbl);
      }});
      edges.forEach((edge,i)=>{{
        const s=nodeById(edge.source),t=nodeById(edge.target);
        const line=document.createElementNS('http://www.w3.org/2000/svg','line');
        line.setAttribute('class','edge');line.setAttribute('id',`edge-${{i}}`);
        line.setAttribute('x1',s.x);line.setAttribute('y1',s.y);
        line.setAttribute('x2',t.x);line.setAttribute('y2',t.y);
        line.setAttribute('stroke',edge.color);line.setAttribute('stroke-width',2.5);line.setAttribute('opacity','0.7');
        viewport.appendChild(line);
      }});
      nodes.forEach(node=>{{
        const g=document.createElementNS('http://www.w3.org/2000/svg','g');
        g.setAttribute('class','node');g.setAttribute('transform',`translate(${{node.x}},${{node.y}})`);g.dataset.id=node.id;
        const circle=document.createElementNS('http://www.w3.org/2000/svg','circle');
        circle.setAttribute('r',32);circle.setAttribute('fill',node.cor);g.appendChild(circle);
        const iata=document.createElementNS('http://www.w3.org/2000/svg','text');
        iata.setAttribute('class','iata');iata.setAttribute('y',5);iata.textContent=node.id;g.appendChild(iata);
        const city=document.createElementNS('http://www.w3.org/2000/svg','text');
        city.setAttribute('class','city');city.setAttribute('y',52);city.textContent=node.label;g.appendChild(city);
        g.addEventListener('mousedown',e=>{{e.stopPropagation();selectedNode=node;}});
        g.addEventListener('mouseenter',e=>{{
          tooltip.innerHTML=`<strong>${{node.label}}</strong><span>Região: ${{node.regiao||'—'}}</span><span>Camada BFS: ${{node.nivel}}</span>`;
          tooltip.classList.add('visible');moveTooltip(e);
        }});
        g.addEventListener('mousemove',moveTooltip);g.addEventListener('mouseleave',hideTooltip);
        viewport.appendChild(g);
      }});
      updateTransform();
    }}
    function updatePositions(){{
      nodes.forEach(node=>{{
        const g=viewport.querySelector(`.node[data-id="${{node.id}}"]`);
        if(g) g.setAttribute('transform',`translate(${{node.x}},${{node.y}})`);
      }});
      edges.forEach((edge,i)=>{{
        const s=nodeById(edge.source),t=nodeById(edge.target);
        const line=document.getElementById(`edge-${{i}}`);
        line.setAttribute('x1',s.x);line.setAttribute('y1',s.y);
        line.setAttribute('x2',t.x);line.setAttribute('y2',t.y);
      }});
    }}
    render();
  </script>
</body>
</html>
"""

    caminho_saida = os.path.join(pasta_saida, arquivo_saida)
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(conteudo_html)

    print(f"[Q8] BFS camadas ({origem}) salvo em: {caminho_saida}")
    return caminho_saida


# ══════════════════════════════════════════════════════════════════════════
# Q9 — APRESENTAÇÃO INTERATIVA DO GRAFO (pyvis)
# ══════════════════════════════════════════════════════════════════════════
def _cor_no_vis(regiao: str) -> dict:
    """Cor de um nó no grafo pyvis, derivada da paleta canônica."""
    base = CORES.get(regiao, "#64748b")
    return {
        "background": base,
        "border": "#ffffff",
        "highlight": {"background": base, "border": "#ffffff"},
    }


def exportar_grafo_interativo(
    caminho_aeroportos: str = "data/aeroportos_data.csv",
    caminho_adjacencias: str = "data/adjacencias_aeroportos.csv",
    caminho_ego: str = "out/ego_aeroportos.csv",
    pasta_saida: str = "out",
    arquivo_saida: str = "grafo_interativo.html",
) -> str:
    import csv as _csv
    from pyvis.network import Network

    info_nos: dict = {}
    try:
        with open(caminho_aeroportos, "r", encoding="utf-8") as f:
            for row in _csv.DictReader(f):
                info_nos[row["iata"]] = {"regiao": row["regiao"], "cidade": row.get("cidade", "")}
    except FileNotFoundError:
        pass

    try:
        with open(caminho_ego, "r", encoding="utf-8") as f:
            for row in _csv.DictReader(f):
                aero = row["aeroporto"]
                info_nos.setdefault(aero, {})
                info_nos[aero]["grau"] = row["grau"]
                info_nos[aero]["densidade_ego"] = row["densidade_ego"]
    except FileNotFoundError:
        pass

    net = Network(
        height="100%", width="100%",
        bgcolor="#07111f", font_color="#e5eefc",
        select_menu=False, cdn_resources="remote",
    )

    nos_adicionados: set = set()
    try:
        with open(caminho_adjacencias, "r", encoding="utf-8") as f:
            for row in _csv.DictReader(f):
                u, v = row["origem"], row["destino"]
                peso = float(row["peso"])
                tipo = row.get("tipo_conexao", "regional")

                for no in (u, v):
                    if no not in nos_adicionados:
                        info = info_nos.get(no, {})
                        regiao = info.get("regiao", "Desconhecida")
                        grau = info.get("grau", "?")
                        dens = (round(float(info.get("densidade_ego", 0.0)), 3)
                                if info.get("densidade_ego") else "?")
                        cidade = info.get("cidade", "")
                        tooltip = (
                            f"<b style='font-size:15px'>{no}</b>"
                            f"{'<br>' + cidade if cidade else ''}"
                            f"<br>Regiao: {regiao}"
                            f"<br>Grau: {grau}"
                            f"<br>Densidade ego: {dens}"
                        )
                        net.add_node(
                            no, label=no, title=tooltip,
                            color=_cor_no_vis(regiao),
                            font={"color": "#ffffff", "size": 15, "bold": True},
                            size=22, borderWidth=2, shadow=True,
                        )
                        nos_adicionados.add(no)

                edge_cor = {
                    "hub_nacional": "#60a5fa",
                    "regional_hub": "#94a3b8",
                    "regional":     "#334155",
                }.get(tipo, "#334155")
                net.add_edge(
                    u, v, value=peso,
                    color={"color": edge_cor, "highlight": "#93c5fd", "opacity": 0.75},
                    width=peso * 1.4, smooth={"type": "continuous"},
                )
    except FileNotFoundError:
        print("Erro: Arquivo adjacencias_aeroportos.csv nao encontrado.")
        return ""

    net.set_options(json.dumps({
        "physics": {
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
                "gravitationalConstant": -55, "centralGravity": 0.006,
                "springLength": 220, "springConstant": 0.18,
                "damping": 0.4, "avoidOverlap": 0.6,
            },
            "minVelocity": 0.5, "stabilization": {"iterations": 180},
        },
        "interaction": {"hover": True, "tooltipDelay": 80, "hideEdgesOnDrag": True},
        "nodes": {"shadow": {"enabled": True, "color": "rgba(0,0,0,0.45)", "size": 12}},
        "edges": {"smooth": {"type": "continuous"}, "shadow": False},
    }))

    os.makedirs(pasta_saida, exist_ok=True)
    caminho_saida = os.path.join(pasta_saida, arquivo_saida)
    net.write_html(caminho_saida)
    print(f"[Q9] {caminho_saida} -> Gerado com sucesso")
    return caminho_saida


# ══════════════════════════════════════════════════════════════════════════
# Q8 — VISUALIZAÇÕES ANALÍTICAS ESTÁTICAS (matplotlib / PNG)
# ══════════════════════════════════════════════════════════════════════════
def _carregar_dados_ego(pasta_dados: str):
    import os as _os
    import pandas as pd
    caminho_csv = _os.path.join(pasta_dados, "ego_aeroportos.csv")
    if not _os.path.exists(caminho_csv):
        print(f"Erro: {caminho_csv} não encontrado. Execute calcular_metricas primeiro.")
        return None
    try:
        return pd.read_csv(caminho_csv)
    except Exception as e:
        print(f"Erro ao ler os dados de ego-rede: {e}")
        return None


def exportar_histograma_graus(pasta_dados: str = "out") -> None:
    """VISUALIZAÇÃO 1: Distribuição de Graus (histograma)."""
    import matplotlib.pyplot as plt

    df_ego = _carregar_dados_ego(pasta_dados)
    if df_ego is None:
        return

    plt.figure(figsize=(8, 5))
    contagem_graus = df_ego["grau"].value_counts().sort_index()
    plt.bar(contagem_graus.index, contagem_graus.values,
            color=CORES["Sudeste"], edgecolor="black", alpha=0.9, width=0.8)
    plt.title("Distribuição de Graus dos Aeroportos", fontsize=14, pad=15, fontweight="bold")
    plt.xlabel("Grau (Número de Interconexões)", fontsize=12)
    plt.ylabel("Frequência (Número de Aeroportos)", fontsize=12)
    plt.xticks(range(int(df_ego["grau"].min()), int(df_ego["grau"].max()) + 1))
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    caminho = os.path.join(pasta_dados, "distribuicao_graus.png")
    plt.savefig(caminho, dpi=300)
    plt.close()
    print(f"[AVD] Histograma salvo em: {caminho}")


def exportar_ranking_conectividade(pasta_dados: str = "out") -> None:
    """VISUALIZAÇÃO 2: Ranking de Aeroportos Mais Conectados (barra ordenada)."""
    import matplotlib.pyplot as plt
    import pandas as pd

    caminho_csv = os.path.join(pasta_dados, "ego_aeroportos.csv")
    if not os.path.exists(caminho_csv):
        print(f"Erro: {caminho_csv} não encontrado. Execute calcular_metricas primeiro.")
        return

    df_ego = pd.read_csv(caminho_csv)
    plt.figure(figsize=(10, 6))
    df_ranking = df_ego.sort_values(by="grau", ascending=True)
    valores_norm = ((df_ranking["grau"] - df_ranking["grau"].min())
                    / (df_ranking["grau"].max() - df_ranking["grau"].min()))
    cores_gradient = plt.cm.Blues(valores_norm * 0.6 + 0.4)
    plt.barh(df_ranking["aeroporto"], df_ranking["grau"], color=cores_gradient, edgecolor="none")
    plt.title("Ranking de Aeroportos por Nível de Conectividade", fontsize=14, pad=15, fontweight="bold")
    plt.xlabel("Grau (Número de Interconexões)", fontsize=12)
    plt.ylabel("Aeroporto (IATA)", fontsize=12)
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()
    caminho = os.path.join(pasta_dados, "ranking_aeroportos.png")
    plt.savefig(caminho, dpi=300)
    plt.close()
    print(f"[AVD] Gráfico de barras salvo em: {caminho}")


def _carregar_dados_regioes(pasta_dados: str):
    caminho_json = os.path.join(pasta_dados, "regioes.json")
    if not os.path.exists(caminho_json):
        print(f"Erro: {caminho_json} não encontrado. Execute calcular_metricas primeiro.")
        return None
    try:
        with open(caminho_json, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler os dados das regiões: {e}")
        return None


def exportar_comparacao_regioes(pasta_dados: str = "out") -> None:
    """VISUALIZAÇÃO 3: Comparação entre Regiões (painel de barras)."""
    import matplotlib.pyplot as plt

    dados = _carregar_dados_regioes(pasta_dados)
    if not dados:
        return

    regioes = [d["regiao"] for d in dados]
    ordens = [d["ordem"] for d in dados]
    tamanhos = [d["tamanho"] for d in dados]
    densidades = [d["densidade"] for d in dados]
    cores = [CORES.get(r, "#64748b") for r in regioes]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Comparação entre Regiões", fontsize=14, fontweight="bold")
    for ax, valores, titulo, ylabel in zip(
        axes,
        [ordens, tamanhos, densidades],
        ["Ordem (Nós)", "Tamanho (Arestas)", "Densidade"],
        ["Quantidade", "Quantidade", "Valor"],
    ):
        ax.bar(regioes, valores, color=cores, edgecolor="black", alpha=0.9)
        ax.set_title(titulo, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.tick_params(axis="x", rotation=20)
        ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    caminho = os.path.join(pasta_dados, "comparacao_regioes.png")
    plt.savefig(caminho, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[AVD] Comparação entre regiões salva em: {caminho}")


# ══════════════════════════════════════════════════════════════════════════
# Q10 — ANÁLISE EXPLORATÓRIA E EXPLANATÓRIA (plotly / HTML interativo)
# ══════════════════════════════════════════════════════════════════════════
_AVD_LAYOUT = dict(
    paper_bgcolor="#07111f",
    plot_bgcolor="#0f1e35",
    font=dict(family="Inter, Segoe UI, Arial, sans-serif", color="#e5eefc"),
    title_font=dict(size=18, color="#f0f9ff"),
    legend=dict(bgcolor="rgba(15,23,42,0.85)", bordercolor="rgba(148,163,184,0.3)", borderwidth=1),
    margin=dict(t=90, b=60, l=60, r=40),
    hoverlabel=dict(bgcolor="#0f172a", bordercolor="rgba(148,163,184,0.4)",
                    font=dict(color="#e5eefc", size=13)),
)


def _avd_carregar(pasta_out, pasta_data):
    import pandas as pd
    df_ego = pd.read_csv(os.path.join(pasta_out, "ego_aeroportos.csv"))
    df_aero = pd.read_csv(os.path.join(pasta_data, "aeroportos_data.csv"))
    df_adj = pd.read_csv(os.path.join(pasta_data, "adjacencias_aeroportos.csv"))
    with open(os.path.join(pasta_out, "global.json"), encoding="utf-8") as f:
        glob = json.load(f)
    with open(os.path.join(pasta_out, "regioes.json"), encoding="utf-8") as f:
        regioes = json.load(f)
    df_ego = (df_ego.merge(df_aero[["iata", "regiao"]], left_on="aeroporto",
                           right_on="iata", how="left").drop(columns="iata"))
    return df_ego, df_aero, df_adj, glob, regioes


def _avd_salvar_html(fig, caminho, titulo_log):
    fig.write_html(caminho, include_plotlyjs="cdn", full_html=True,
                   config={"displayModeBar": True, "scrollZoom": True})
    print(f"[Q10] {titulo_log} salvo -> {caminho}")


def _avd_exp1_distribuicao(df_ego, pasta):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    regioes_ord = (df_ego.groupby("regiao")["grau"].median()
                   .sort_values(ascending=False).index.tolist())
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Histograma dos graus", "Distribuicao por regiao"),
                        horizontal_spacing=0.12)
    fig.add_trace(go.Histogram(
        x=df_ego["grau"], name="Aeroportos",
        marker=dict(color=CORES["Sudeste"], line=dict(color="#07111f", width=1)),
        opacity=0.9, hovertemplate="Grau %{x}: %{y} aeroportos<extra></extra>",
    ), row=1, col=1)
    media = df_ego["grau"].mean()
    fig.add_vline(x=media, line=dict(color=CORES["Nordeste"], dash="dash", width=2),
                  annotation_text=f"Media = {media:.1f}",
                  annotation_font=dict(color=CORES["Nordeste"]), row=1, col=1)
    for reg in regioes_ord:
        fig.add_trace(go.Box(
            y=df_ego[df_ego["regiao"] == reg]["grau"],
            name=reg, marker_color=CORES[reg], line_color=CORES[reg], boxmean=True,
            hovertemplate=f"<b>{reg}</b><br>Grau: %{{y}}<extra></extra>",
        ), row=1, col=2)
    fig.update_layout(**_AVD_LAYOUT, height=520, showlegend=True,
                      title=dict(text="Exploratorio 1 - Distribuicao dos Graus na Rede",
                                 x=0.5, xanchor="center"))
    for col, xt, yt in [(1, "Grau", "Qtd aeroportos"), (2, "Regiao", "Grau")]:
        fig.update_xaxes(title_text=xt, gridcolor="rgba(148,163,184,0.1)", row=1, col=col)
        fig.update_yaxes(title_text=yt, gridcolor="rgba(148,163,184,0.1)", row=1, col=col)
    _avd_salvar_html(fig, os.path.join(pasta, "q10_exp1_distribuicao_graus.html"), "Exploratorio 1")


def _avd_exp2_composicao(df_ego, df_adj, pasta):
    import pandas as pd
    import plotly.graph_objects as go
    TIPOS = ["regional", "regional_hub", "hub_nacional"]
    contagem = {}
    for _, row in df_adj.iterrows():
        for no in [row["origem"], row["destino"]]:
            if no not in contagem:
                contagem[no] = {t: 0 for t in TIPOS}
            contagem[no][row["tipo_conexao"]] += 1
    df_cont = (pd.DataFrame(contagem).T.reset_index()
               .rename(columns={"index": "aeroporto"})
               .merge(df_ego[["aeroporto", "regiao", "grau"]], on="aeroporto")
               .sort_values("grau", ascending=False))
    for t in TIPOS:
        if t not in df_cont.columns:
            df_cont[t] = 0
    fig = go.Figure()
    for tipo in TIPOS:
        label = tipo.replace("_", " ").capitalize()
        fig.add_trace(go.Bar(
            x=df_cont["aeroporto"], y=df_cont[tipo].fillna(0), name=label,
            marker_color=CORES_TIPO[tipo], customdata=df_cont["regiao"],
            hovertemplate=f"<b>%{{x}}</b><br>{label}: %{{y}}<br>Regiao: %{{customdata}}<extra></extra>",
        ))
    fig.update_layout(**_AVD_LAYOUT, barmode="stack", height=520,
                      title=dict(text="Exploratorio 2 - Composicao das Conexoes por Tipo",
                                 x=0.5, xanchor="center"),
                      xaxis=dict(title="Aeroporto", tickangle=-45, gridcolor="rgba(148,163,184,0.1)"),
                      yaxis=dict(title="No. de conexoes", gridcolor="rgba(148,163,184,0.1)"))
    _avd_salvar_html(fig, os.path.join(pasta, "q10_exp2_composicao_conexoes.html"), "Exploratorio 2")


def _avd_expl1_ranking(df_ego, pasta):
    import plotly.graph_objects as go
    df_sorted = df_ego.sort_values("grau", ascending=True)
    colors = [CORES[r] for r in df_sorted["regiao"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_sorted["grau"], y=df_sorted["aeroporto"], orientation="h",
        marker=dict(color=colors, line=dict(color="#07111f", width=0.5)),
        customdata=df_sorted[["regiao", "densidade_ego"]].values,
        hovertemplate=("<b>%{y}</b><br>Grau: %{x} conexoes<br>"
                       "Regiao: %{customdata[0]}<br>"
                       "Densidade ego: %{customdata[1]:.3f}<extra></extra>"),
        text=df_sorted["grau"].astype(int), textposition="outside",
        textfont=dict(color="#e5eefc", size=11), name="Grau",
    ))
    media = df_ego["grau"].mean()
    fig.add_vline(x=media, line=dict(color="#94a3b8", dash="dash", width=1.5),
                  annotation_text=f"Media: {media:.1f}", annotation_font=dict(color="#94a3b8"))
    for regiao, cor in CORES.items():
        fig.add_trace(go.Bar(x=[None], y=[None], name=regiao, marker_color=cor, showlegend=True))
    fig.update_layout(**_AVD_LAYOUT, height=max(480, len(df_sorted) * 26), showlegend=True,
                      title=dict(text="Explanatorio 1 - Ranking de Hubs da Rede", x=0.5, xanchor="center"),
                      xaxis=dict(title="Grau (conexoes diretas)", gridcolor="rgba(148,163,184,0.1)"),
                      yaxis=dict(title="Aeroporto", gridcolor="rgba(148,163,184,0.1)"))
    _avd_salvar_html(fig, os.path.join(pasta, "q10_expl1_ranking_hubs.html"), "Explanatorio 1")


def _avd_expl2_comparacao(df_ego, regioes, pasta):
    import pandas as pd
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    df_r = pd.DataFrame(regioes)
    grau_medio = (df_ego.groupby("regiao")["grau"].mean().rename("grau_medio").reset_index())
    df_r = df_r.merge(grau_medio, on="regiao")
    metricas = [("ordem", "No. de aeroportos", "Aeroportos"),
                ("tamanho", "No. de arestas", "Arestas internas"),
                ("grau_medio", "Grau medio", "Grau medio")]
    fig = make_subplots(rows=1, cols=3, subplot_titles=[m[2] for m in metricas], horizontal_spacing=0.10)
    for idx, (col, ylabel, _title) in enumerate(metricas, start=1):
        df_plot = df_r.sort_values(col, ascending=False)
        colors = [CORES[r] for r in df_plot["regiao"]]
        labels = [f"{v:.1f}" if col == "grau_medio" else str(int(v)) for v in df_plot[col]]
        fig.add_trace(go.Bar(
            x=df_plot["regiao"], y=df_plot[col],
            marker=dict(color=colors, line=dict(color="#07111f", width=0.5)),
            text=labels, textposition="outside", textfont=dict(color="#e5eefc", size=11),
            hovertemplate=f"<b>%{{x}}</b><br>{ylabel}: %{{y}}<extra></extra>", showlegend=False,
        ), row=1, col=idx)
        fig.update_xaxes(tickangle=-22, gridcolor="rgba(148,163,184,0.1)", row=1, col=idx)
        fig.update_yaxes(title_text=ylabel, gridcolor="rgba(148,163,184,0.1)", row=1, col=idx)
    fig.update_layout(**_AVD_LAYOUT, height=500, showlegend=False,
                      title=dict(text="Explanatorio 2 - Comparacao entre Regioes", x=0.5, xanchor="center"))
    _avd_salvar_html(fig, os.path.join(pasta, "q10_expl2_comparacao_regioes.html"), "Explanatorio 2")


def exportar_avd_visualizacoes(pasta_saida: str = "out", pasta_data: str = "data") -> None:
    """Q10 — gera as 4 visualizações interativas (2 exploratórias + 2 explanatórias)."""
    os.makedirs(pasta_saida, exist_ok=True)
    df_ego, _, df_adj, _glob, regioes = _avd_carregar(pasta_saida, pasta_data)
    _avd_exp1_distribuicao(df_ego, pasta_saida)
    _avd_exp2_composicao(df_ego, df_adj, pasta_saida)
    _avd_expl1_ranking(df_ego, pasta_saida)
    _avd_expl2_comparacao(df_ego, regioes, pasta_saida)
    print("[Q10] 4 visualizacoes interativas geradas em out/\n")


if __name__ == "__main__":
    exportar_arvore_percurso()
