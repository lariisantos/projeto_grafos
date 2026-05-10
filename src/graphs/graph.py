class Grafo:
    # Construtor
    def __init__(self):
        self.adj = {} # dic que armazenará as conexões: "chave" = IATA e  "valor" outro dic contendo seus vizinhos e os pesos dos voos.
        self.nodes_info = {} # dicionário auxiliar para guardar metadados dos nós

    def adicionar_vertice(self, iata, info):
        if iata not in self.adj: 
            self.adj[iata] = {} # Inicializa a entrada do aeroporto na lista de adjacência
            self.nodes_info[iata] = info # Salva as informações extras

    def adicionar_aresta(self, u, v, peso):
        # Como o grafo de aeroportos geralmente é não-direcionado:
        if u in self.adj and v in self.adj:
            self.adj[u][v] = float(peso) # No dicionário do aeroporto u, adicionamos o aeroporto v como vizinho e atribuímos o peso.
            self.adj[v][u] = float(peso) # garante o voo de volta, aresta bidirencional

