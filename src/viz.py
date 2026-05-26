from __future__ import annotations

import heapq
import html
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graphs.io import carregar_grafo


ROTAS_OBRIGATORIAS = [ #se precisar é só adicionar mais rotas
    ("REC", "POA"),  # Recife -> Porto Alegre
    ("MAO", "CGH"),  # Manaus -> São Paulo, conforme data/rotas.csv
]


def menor_caminho_dijkstra(grafo, origem: str, destino: str) -> tuple[float, list[str]]:
    origem = origem.strip().upper()
    destino = destino.strip().upper()

    if origem not in grafo.adj:
        raise ValueError(f"Aeroporto de origem não encontrado no grafo: {origem}")
    if destino not in grafo.adj:
        raise ValueError(f"Aeroporto de destino não encontrado no grafo: {destino}")

    fila = [(0.0, origem, [origem])]
    melhor_distancia = {origem: 0.0}

    while fila:
        custo_atual, no_atual, caminho = heapq.heappop(fila)

        if no_atual == destino:
            return custo_atual, caminho

        if custo_atual > melhor_distancia.get(no_atual, float("inf")):
            continue

        for vizinho, peso in grafo.adj[no_atual].items():
            novo_custo = custo_atual + float(peso)

            if novo_custo < melhor_distancia.get(vizinho, float("inf")):
                melhor_distancia[vizinho] = novo_custo
                heapq.heappush(fila, (novo_custo, vizinho, caminho + [vizinho]))

    return float("inf"), []


def construir_subgrafo_percursos(grafo, rotas: list[tuple[str, str]]):
    caminhos = []
    arestas = set()
    nos = set()

    for origem, destino in rotas:
        custo, caminho = menor_caminho_dijkstra(grafo, origem, destino)

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


if __name__ == "__main__":
    exportar_arvore_percurso()
