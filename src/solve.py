import csv
import json
import os
import sys

import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graphs.algorithms import dijkstra

from graphs.io import carregar_aeroportos, carregar_grafo
from graphs.graph import Grafo
from graphs.metrics import metricas_subgrafo, ego_rede

from pyvis.network import Network

def gerar_arquivo_adjacencias():
    df = carregar_aeroportos('data/aeroportos_data.csv')

    hubs = {
        'Sudeste': 'GRU',
        'Nordeste': 'REC',
        'Norte': 'MAO',
        'Sul': 'POA',
        'Centro-Oeste': 'BSB',
    }

    adjacencias = []

    for regiao, grupo in df.groupby('regiao'):
        lista_aeroportos = grupo['iata'].tolist()

        hub_da_regiao = hubs.get(regiao)
        if hub_da_regiao not in lista_aeroportos:
            print(f"Aviso: Hub {hub_da_regiao} não encontrado na região {regiao}!")

        for i in range(len(lista_aeroportos)):
            for j in range(i + 1, len(lista_aeroportos)):
                u, v = lista_aeroportos[i], lista_aeroportos[j]

                tipo = "regional"
                just = "Mesma região"
                peso = 1.0

                if u == hub_da_regiao or v == hub_da_regiao:
                    tipo = "regional_hub"
                    just = f"Conexão direta com hub {hub_da_regiao}"
                    peso = 1.5

                adjacencias.append([u, v, tipo, just, peso])

    lista_hubs = list(hubs.values())
    for i in range(len(lista_hubs)):
        for j in range(i + 1, len(lista_hubs)):
            adjacencias.append([lista_hubs[i], lista_hubs[j], "hub_nacional", "Conexão entre hubs regionais", 2.0])

    df_adj = pd.DataFrame(adjacencias, columns=['origem', 'destino', 'tipo_conexao', 'justificativa', 'peso'])
    df_adj.to_csv('data/adjacencias_aeroportos.csv', index=False)
    print("Sucesso: Arquivo 'adjacencias_aeroportos.csv' gerado com dados validados.")


def calcular_metricas(
    caminho_aeroportos: str = 'data/aeroportos_data.csv',
    caminho_adjacencias: str = 'data/adjacencias_aeroportos.csv',
    pasta_saida: str = 'out',
) -> tuple:
    os.makedirs(pasta_saida, exist_ok=True)

    grafo, df = carregar_grafo(caminho_aeroportos, caminho_adjacencias)

    todos_nos = set(grafo.adj.keys())
    m_global = metricas_subgrafo(grafo, todos_nos)
    with open(os.path.join(pasta_saida, 'global.json'), 'w', encoding='utf-8') as f:
        json.dump(m_global, f, ensure_ascii=False, indent=2)
    print(f"[Q3] global.json  → ordem={m_global['ordem']}, tamanho={m_global['tamanho']}, densidade={m_global['densidade']:.4f}")

    mapa_regioes: dict[str, set] = {}
    for _, row in df.iterrows():
        mapa_regioes.setdefault(row['regiao'], set()).add(row['iata'])

    lista_regioes = []
    for regiao in sorted(mapa_regioes.keys()):
        nos_regiao = mapa_regioes[regiao]
        m = metricas_subgrafo(grafo, nos_regiao)
        lista_regioes.append({'regiao': regiao, **m})
        print(f"[Q3]   {regiao:15s} → ordem={m['ordem']}, tamanho={m['tamanho']}, densidade={m['densidade']:.4f}")

    with open(os.path.join(pasta_saida, 'regioes.json'), 'w', encoding='utf-8') as f:
        json.dump(lista_regioes, f, ensure_ascii=False, indent=2)
    print(f"[Q3] regioes.json → {len(lista_regioes)} regiões")

    rows_ego = [ego_rede(grafo, no) for no in sorted(grafo.adj.keys())]
    df_ego = pd.DataFrame(rows_ego, columns=['aeroporto', 'grau', 'ordem_ego', 'tamanho_ego', 'densidade_ego'])
    df_ego.to_csv(os.path.join(pasta_saida, 'ego_aeroportos.csv'), index=False)
    print(f"[Q3] ego_aeroportos.csv → {len(rows_ego)} aeroportos")

    return m_global, lista_regioes, rows_ego

def calcular_rotas_dijkstra():

    grafo, _ = carregar_grafo('data/aeroportos_data.csv', 'data/adjacencias_aeroportos.csv')
    rotas = []
    
    try:
        with open('data/rotas.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('origem') and row.get('destino'):
                    rotas.append((row['origem'].strip(), row['destino'].strip()))
    except FileNotFoundError:
        pass

    resultados = []
    for orig, dest in rotas:
        if orig not in grafo.adj or dest not in grafo.adj:
            resultados.append([orig, dest, float('inf'), "Sem caminho viável"])
            print(f"[Q6]   {orig} → {dest:3s} → Erro: Aeroporto não encontrado no grafo.")
            continue
            
        custo, caminho = dijkstra(grafo, orig, dest)
        str_caminho = " -> ".join(caminho) if caminho else "Sem caminho viável"
        
        resultados.append([orig, dest, custo, str_caminho])
        print(f"[Q6]   {orig} → {dest:3s} → custo={custo:.1f}, caminho=[{str_caminho}]")

    os.makedirs('out', exist_ok=True)
    with open('out/distancias_rotas.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['origem', 'destino', 'custo', 'caminho'])
        for res in resultados:
            writer.writerow(res)
            
    print(f"[Q6] distancias_rotas.csv → {len(resultados)} rotas processadas")
    grafo, _ = carregar_grafo('data/aeroportos_data.csv', 'data/adjacencias_aeroportos.csv')
    rotas = []
    
    try:
        with open('data/rotas.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('origem') and row.get('destino'):
                    rotas.append((row['origem'].strip(), row['destino'].strip()))
    except FileNotFoundError:
        pass

    resultados = []
    for orig, dest in rotas:
        if orig not in grafo.adj or dest not in grafo.adj:
            resultados.append([orig, dest, float('inf'), "Sem caminho viável"])
            continue
            
        custo, caminho = dijkstra(grafo, orig, dest)
        str_caminho = " -> ".join(caminho) if caminho else "Sem caminho viável"
        
        resultados.append([orig, dest, custo, str_caminho])

    os.makedirs('out', exist_ok=True)
    with open('out/distancias_rotas.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['origem', 'destino', 'custo', 'caminho'])
        for res in resultados:
            writer.writerow(res)
   
def gerar_grafo_interativo():
    info_nos = {}
    try:
        with open('data/aeroportos_data.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                info_nos[row['iata']] = {'regiao': row['regiao']}
    except FileNotFoundError:
        pass

    try:
        with open('out/ego_aeroportos.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                aero = row['aeroporto']
                if aero not in info_nos:
                    info_nos[aero] = {}
                info_nos[aero]['grau'] = row['grau']
                info_nos[aero]['densidade_ego'] = row['densidade_ego']
    except FileNotFoundError:
        pass

    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black", select_menu=False, cdn_resources='remote')

    nos_adicionados = set()
    try:
        with open('data/adjacencias_aeroportos.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                u = row['origem']
                v = row['destino']
                peso = float(row['peso'])
                
                for no in (u, v):
                    if no not in nos_adicionados:
                        info = info_nos.get(no, {})
                        regiao = info.get('regiao', 'Desconhecida')
                        grau = info.get('grau', '?')
                        densidade = round(float(info.get('densidade_ego', 0.0)), 3) if info.get('densidade_ego') else '?'
                        
                        tooltip = f"Aeroporto: {no}\n Região: {regiao}\n Grau: {grau}\n Densidade Ego: {densidade}"
                        net.add_node(no, label=no, title=tooltip)
                        nos_adicionados.add(no)
                
                net.add_edge(u, v, value=peso)
    except FileNotFoundError:
        print("Erro: Arquivo adjacencias_aeroportos.csv não encontrado.")
        return

    os.makedirs('out', exist_ok=True)
    caminho_html = 'out/grafo_interativo.html'
    net.write_html(caminho_html)

    # --- INJEÇÃO DE DOIS DROPDOWNS PARA CAMINHO MÍNIMO ---
    rotas_dict = {}
    airports_set = set()
    try:
        with open('out/distancias_rotas.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                orig = row['origem']
                dest = row['destino']
                custo = row['custo']
                caminho_str = row['caminho']
                
                airports_set.add(orig)
                airports_set.add(dest)
                
                if caminho_str and caminho_str != "Sem caminho viável":
                    caminho_list = [x.strip() for x in caminho_str.split('->')]
                else:
                    caminho_list = []
                    
                rotas_dict[f"{orig}->{dest}"] = {
                    "custo": custo,
                    "caminho": caminho_list
                }
    except FileNotFoundError:
        print("Aviso: out/distancias_rotas.csv não encontrado para embutir no menu.")

    airports_sorted = sorted(list(airports_set))
    import json
    rotas_json = json.dumps(rotas_dict, ensure_ascii=False)
    airports_json = json.dumps(airports_sorted, ensure_ascii=False)

    snippet_html_js = f"""
    <!-- Injeção dos Dropdowns de Rota Personalizados -->
    <div id="menu-rotas-duplo" style="position: absolute; top: 60px; left: 10px; z-index: 1000; background-color: rgba(255, 255, 255, 0.95); padding: 15px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.15); font-family: Arial, sans-serif; border: 1px solid #bbb; width: 260px;">
        <h4 style="margin-top: 0; margin-bottom: 12px; color: #222; border-bottom: 2px solid #007bff; padding-bottom: 5px; font-size: 14px;">Exibir Caminho Mínimo</h4>
        <div style="margin-bottom: 8px;">
            <label for="select-origem" style="font-size: 11px; font-weight: bold; color: #444; display: block; margin-bottom: 3px;">Origem:</label>
            <select id="select-origem" style="width: 100%; padding: 6px; border-radius: 4px; border: 1px solid #999; background: white; font-size: 13px;"></select>
        </div>
        <div style="margin-bottom: 12px;">
            <label for="select-destino" style="font-size: 11px; font-weight: bold; color: #444; display: block; margin-bottom: 3px;">Destino:</label>
            <select id="select-destino" style="width: 100%; padding: 6px; border-radius: 4px; border: 1px solid #999; background: white; font-size: 13px;"></select>
        </div>
        <div id="info-rota-status" style="font-size: 12px; margin-top: 10px; padding-top: 8px; border-top: 1px solid #ddd; color: #333; min-height: 45px; line-height: 1.4;">
            Selecione origem e destino para destacar o caminho calculado via Dijkstra.
        </div>
    </div>

    <script type="text/javascript">
    document.addEventListener("DOMContentLoaded", function() {{
        const rotasData = {rotas_json};
        const aeroportos = {airports_json};
        
        const selOrigem = document.getElementById("select-origem");
        const selDestino = document.getElementById("select-destino");
        const infoRota = document.getElementById("info-rota-status");
        
        // Preencher as caixas de seleção
        let optionsHtml = '<option value="">-- Selecione --</option>';
        aeroportos.forEach(aero => {{
            optionsHtml += `<option value="${{aero}}">${{aero}}</option>`;
        }});
        selOrigem.innerHTML = optionsHtml;
        selDestino.innerHTML = optionsHtml;
        
        let originalEdgeColors = {{}};
        let originalEdgeWidths = {{}};
        let originalNodeColors = {{}};
        
        function salvarEstilosOriginais() {{
            if (typeof edges !== 'undefined' && Object.keys(originalEdgeColors).length === 0) {{
                edges.forEach(e => {{
                    originalEdgeColors[e.id] = e.color || '#848484';
                    originalEdgeWidths[e.id] = e.width || 1;
                }});
            }}
            if (typeof nodes !== 'undefined' && Object.keys(originalNodeColors).length === 0) {{
                nodes.forEach(n => {{
                    originalNodeColors[n.id] = n.color || null;
                }});
            }}
        }}
        
        function destacarRotaSelecionada() {{
            salvarEstilosOriginais();
            const orig = selOrigem.value;
            const dest = selDestino.value;
            
            // Limpar/Resetar para o visual original
            if (typeof nodes !== 'undefined') {{
                nodes.forEach(n => {{
                    nodes.update({{id: n.id, color: originalNodeColors[n.id], borderWidth: 1}});
                }});
            }}
            if (typeof edges !== 'undefined') {{
                edges.forEach(e => {{
                    edges.update({{id: e.id, color: originalEdgeColors[e.id], width: originalEdgeWidths[e.id]}});
                }});
            }}
            
            if (!orig || !dest) {{
                infoRota.innerHTML = "Selecione origem e destino para destacar o caminho calculado via Dijkstra.";
                return;
            }}
            
            if (orig === dest) {{
                infoRota.innerHTML = "<strong>Origem e destino idênticos.</strong><br>Custo: 0.0";
                if (typeof nodes !== 'undefined') {{
                    nodes.update({{id: orig, color: {{ background: '#ffc107', border: '#ff9800' }}, borderWidth: 3}});
                }}
                return;
            }}
            
            const chave = `${{orig}}->${{dest}}`;
            const rota = rotasData[chave];
            
            if (!rota || !rota.caminho || rota.caminho.length === 0) {{
                infoRota.innerHTML = "<span style='color: #dc3545;'><strong>Sem caminho viável cadastrado.</strong></span>";
                return;
            }}
            
            infoRota.innerHTML = `<strong>Custo total:</strong> ${{rota.custo}}<br><strong>Percurso:</strong><br>${{rota.caminho.join(' → ')}}`;
            
            // Destacar os vértices participantes
            rota.caminho.forEach((noId, idx) => {{
                let corNo = '#ff4d4d';
                let corBorda = '#dc3545';
                if (idx === 0) {{ corNo = '#28a745'; corBorda = '#1e7e34'; }} // Origem Verde
                if (idx === rota.caminho.length - 1) {{ corNo = '#007bff'; corBorda = '#0062cc'; }} // Destino Azul
                
                nodes.update({{
                    id: noId, 
                    color: {{ background: corNo, border: corBorda, highlight: {{ background: corNo, border: corBorda }} }},
                    borderWidth: 3
                }});
            }});
            
            // Destacar as arestas participantes
            for (let i = 0; i < rota.caminho.length - 1; i++) {{
                const u = rota.caminho[i];
                const v = rota.caminho[i+1];
                
                const arestas = edges.get({{
                    filter: function (item) {{
                        return (item.from === u && item.to === v) || (item.from === v && item.to === u);
                    }}
                }});
                
                arestas.forEach(e => {{
                    edges.update({{
                        id: e.id, 
                        color: '#dc3545', 
                        width: 5
                    }});
                }});
            }}
        }}
        
        selOrigem.addEventListener("change", destacarRotaSelecionada);
        selDestino.addEventListener("change", destacarRotaSelecionada);
    }});
    </script>
    """

    try:
        with open(caminho_html, 'r', encoding='utf-8') as file:
            conteudo = file.read()
        
        conteudo_modificado = conteudo.replace("</body>", f"{snippet_html_js}\n</body>")
        
        with open(caminho_html, 'w', encoding='utf-8') as file:
            file.write(conteudo_modificado)
        print("[Q9] Menu de rotas duplo injetado com sucesso no HTML.")
    except Exception as e:
        print(f"Erro ao injetar menu personalizado no HTML: {e}")

def gerar_arvore_percurso( 
    caminho_aeroportos: str = 'data/aeroportos_data.csv',
    caminho_adjacencias: str = 'data/adjacencias_aeroportos.csv',
    pasta_saida: str = 'out',
) -> str:
    from viz import exportar_arvore_percurso

    return exportar_arvore_percurso(
        caminho_aeroportos=caminho_aeroportos,
        caminho_adjacencias=caminho_adjacencias,
        pasta_saida=pasta_saida,
    )

def gerar_visualizacoes_avd(pasta_dados: str = 'out'):
    caminho_csv = os.path.join(pasta_dados, 'ego_aeroportos.csv')
    
    if not os.path.exists(caminho_csv):
        print(f"Erro: {caminho_csv} não encontrado. Execute calcular_metricas_q3 primeiro.")
        return

    df_ego = pd.read_csv(caminho_csv)
    
    # --- VISUALIZAÇÃO 1: Distribuição de Graus (Histograma) ---
    plt.figure(figsize=(8, 5))
    
    # Contagem da frequência de cada grau ordenado de forma ascedente
    contagem_graus = df_ego['grau'].value_counts().sort_index()
    
    plt.bar(contagem_graus.index, 
            contagem_graus.values, 
            color='#4c72b0', 
            edgecolor='black', 
            alpha=0.9, 
            width=0.8)
    
    plt.title('Distribuição de Graus dos Aeroportos', fontsize=14, pad=15, fontweight='bold')
    plt.xlabel('Grau (Número de Interconexões)', fontsize=12)
    plt.ylabel('Frequência (Número de Aeroportos)', fontsize=12)
    
    plt.xticks(range(int(df_ego['grau'].min()), int(df_ego['grau'].max()) + 1))
    plt.grid(axis='y', linestyle='--', alpha=0.7) # Linhas de grade na horizontal
    
    plt.tight_layout()
    caminho_hist = os.path.join(pasta_dados, 'distribuicao_graus.png')
    plt.savefig(caminho_hist, dpi=300)
    plt.close()
    print(f"[AVD] Histograma salvo em: {caminho_hist}")

    # --- VISUALIZAÇÃO 2: Ranking de Aeroportos Mais Conectados (Barra Ordenada) ---
    plt.figure(figsize=(10, 6))
    
    # Ordena os dados do menor para o maior (para que o maior fique no topo do gráfico horizontal)
    df_ranking = df_ego.sort_values(by='grau', ascending=True)
    
    # Criando um degradê de azul usando um colormap do Matplotlib
    valores_norm = (df_ranking['grau'] - df_ranking['grau'].min()) / (df_ranking['grau'].max() - df_ranking['grau'].min())
    cores_gradient = plt.cm.Blues(valores_norm * 0.6 + 0.4) 
    
    # Gráfico de barras horizontais
    plt.barh(df_ranking['aeroporto'], df_ranking['grau'], color=cores_gradient, edgecolor='none')
    
    # Customização de AVD
    plt.title('Ranking de Aeroportos por Nível de Conectividade', fontsize=14, pad=15, fontweight='bold')
    plt.xlabel('Grau (Número de Interconexões)', fontsize=12)
    plt.ylabel('Aeroporto (IATA)', fontsize=12)
    plt.grid(axis='x', linestyle='--', alpha=0.7) # Linhas de grade verticais para ajudar a ler o ranking
    
    plt.tight_layout()
    caminho_barra = os.path.join(pasta_dados, 'ranking_aeroportos.png')
    plt.savefig(caminho_barra, dpi=300)
    plt.close()
    print(f"[AVD] Gráfico de barras salvo em: {caminho_barra}")

def main():
    try:
        gerar_arquivo_adjacencias()
        calcular_rotas_dijkstra()
        gerar_grafo_interativo()
        calcular_metricas()
        gerar_arvore_percurso() 
        gerar_visualizacoes_avd()
    except Exception as e:
        print(f"Falha na execução: {e}")
        raise


if __name__ == "__main__":
    main()