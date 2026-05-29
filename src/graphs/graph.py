class Grafo:
    def __init__(self):
        self.adj = {} # dic que armazenará as conexões: "chave" = IATA e  "valor" outro dic contendo seus vizinhos e os pesos dos voos.
        self.nodes_info = {} # dic para guardar cidade e regiao

    def adicionar_vertice(self, iata, info):
        if iata not in self.adj: 
            self.adj[iata] = {} # Inicializa a entrada do aeroporto na lista de adjacência
            self.nodes_info[iata] = info # Salva as informações extras

    def adicionar_aresta(self, origem, destino, peso):
        """
        Estabelece uma conexão bidirecional entre dois aeroportos com um peso definido.
        """
        if origem in self.adj and destino in self.adj:
            self.adj[origem][destino] = float(peso) 
            self.adj[destino][origem] = float(peso) 

