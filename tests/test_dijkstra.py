import os
import csv
import heapq
from collections import defaultdict

def dijkstra(grafo, origem, destino):
    fila = [(0.0, origem, [origem])]
    visitados = set()
    
    while fila:
        custo, no_atual, caminho = heapq.heappop(fila)
        
        if no_atual == destino:
            return custo, caminho
            
        if no_atual not in visitados:
            visitados.add(no_atual)
            
            for vizinho, peso in grafo.get(no_atual, {}).items():
                if vizinho not in visitados:
                    heapq.heappush(fila, (custo + peso, vizinho, caminho + [vizinho]))
                    
    return float('inf'), []

def main():
    # Garantir que os diretórios existam
    os.makedirs('data', exist_ok=True)
    os.makedirs('out', exist_ok=True)

    arquivo_rotas = './data/rotas.csv'
    arquivo_adjacencias = './data/adjacencias_aeroportos.csv'
    arquivo_saida = 'out/distancias_rotas.csv'

    # 1. Carregar as rotas do arquivo (se ele não existir, cria um modelo básico)
    rotas = []
    try:
        with open(arquivo_rotas, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Ignorar linhas em branco caso existam
                if row.get('origem') and row.get('destino'):
                    rotas.append((row['origem'].strip(), row['destino'].strip()))
    except FileNotFoundError:
        print(f"O arquivo '{arquivo_rotas}' não existia.")
        print("Criando um arquivo modelo com os pares obrigatórios para você editar...")
        rotas_iniciais = [
            ('REC', 'POA'),
            ('MAO', 'GRU'),
            ('BSB', 'FLN'),
            ('FOR', 'CWB'),
            ('GYN', 'VIX')
        ]
        with open(arquivo_rotas, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['origem', 'destino'])
            for r in rotas_iniciais:
                writer.writerow(r)
        rotas = rotas_iniciais
        print(f"Pronto! Você pode editar '{arquivo_rotas}' futuramente.\n")

    # 2. Construir o grafo
        grafo = defaultdict(dict)
    try:
        with open(arquivo_adjacencias, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                orig = row['origem']
                dest = row['destino']
                peso = float(row['peso'])
                grafo[orig][dest] = peso
                grafo[dest][orig] = peso
    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo_adjacencias}' não foi encontrado.")
        return

    # 3. Calcular caminhos para as rotas lidas do CSV
    resultados = []
    print(f"Processando {len(rotas)} rotas encontradas...\n")
    for orig, dest in rotas:
        if orig not in grafo or dest not in grafo:
             resultados.append([orig, dest, float('inf'), f"Erro: Aeroporto não existe no grafo"])
             continue
             
        custo, caminho = dijkstra(grafo, orig, dest)
        str_caminho = " -> ".join(caminho) if caminho else "Sem caminho viável"
        resultados.append([orig, dest, custo, str_caminho])

    # 4. Atualizar o arquivo out/distancias_rotas.csv
    with open(arquivo_saida, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['origem', 'destino', 'custo', 'caminho'])
        for res in resultados:
            writer.writerow(res)
            
    print(f"Arquivo '{arquivo_saida}' ATUALIZADO com sucesso!\n")
    
    # Mostrar um resumo no console
    print(f"{'Origem':<8} | {'Destino':<8} | {'Custo':<6} | Caminho")
    print("-" * 65)
    for res in resultados:
        print(f"{res[0]:<8} | {res[1]:<8} | {res[2]:<6} | {res[3]}")

if __name__ == '__main__':
    main()