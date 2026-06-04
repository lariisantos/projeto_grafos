import heapq

class Grafo:
    def __init__(self, adj):
        self.adj = adj

def dijkstra(grafo, origem, destino):
    fila = [(0.0, origem, [origem])]
    visitados = set()
    
    while fila:
        custo, no_atual, caminho = heapq.heappop(fila)
        
        if no_atual == destino:
            return custo, caminho
            
        if no_atual not in visitados:
            visitados.add(no_atual)
            
            for vizinho, peso in grafo.adj.get(no_atual, {}).items():
                if peso < 0:
                    continue
                    
                if vizinho not in visitados:
                    heapq.heappush(fila, (custo + peso, vizinho, caminho + [vizinho]))
                    
    return float('inf'), []

def testar():
    adj_negativo = {
        'A': {'B': 2, 'C': 1},
        'B': {'C': -5},
        'C': {}
    }
    grafo_negativo = Grafo(adj_negativo)
    custo2, caminho2 = dijkstra(grafo_negativo, 'A', 'C')
    
    print("--- TESTE DIJKSTRA: GRAFO COM PESO NEGATIVO ---")
    print(f"Caminho A -> C: {caminho2} | Custo: {custo2}")

if __name__ == "__main__":
    testar()