class Grafo:
    def __init__(self, adj):
        self.adj = adj

def bellman_ford(grafo, origem, destino):
    distancias = {no: float('inf') for no in grafo.adj}
    caminhos = {no: [] for no in grafo.adj}
    
    distancias[origem] = 0
    caminhos[origem] = [origem]
    
    nos = list(grafo.adj.keys())
    
    for _ in range(len(nos) * 2):
        houve_mudanca = False
        for u in nos:
            if distancias[u] == float('inf'):
                continue
            for v, peso in grafo.adj.get(u, {}).items():
                
                if caminhos[u].count(v) < 2:
                    if distancias[u] + peso < distancias[v]:
                        distancias[v] = distancias[u] + peso
                        caminhos[v] = caminhos[u] + [v]
                        houve_mudanca = True
                        
        if not houve_mudanca:
            break
            
    if distancias[destino] == float('inf'):
        return float('inf'), []
        
    return distancias[destino], caminhos[destino]

def testar():
    adj_ciclo = {
        'A': {'B': 1},
        'B': {'C': -5},
        'C': {'B': -5, 'D': 2},
        'D': {}
    }
    
    grafo_ciclo = Grafo(adj_ciclo)
    
    custo, caminho = bellman_ford(grafo_ciclo, 'A', 'D')
    
    str_caminho = " -> ".join(caminho) if caminho else "Nenhum caminho encontrado"
    
    print("--- TESTE BELLMAN-FORD: CICLO NEGATIVO (1 VOLTA) ---")
    print(f"Origem: A | Destino: D")
    print(f"Rota Dinâmica: {str_caminho}")
    print(f"Custo Final: {custo}")
if __name__ == "__main__":
    testar()