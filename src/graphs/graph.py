class Grafo:
    def __init__(self):
        self.adj = {} # "chave" = id_vertice e "valor" = dic com vizinhos e pesos
        self.nodes_info = {} # dic para guardar informações extras do vértice

    def adicionar_vertice(self, id_vertice, info):
        if id_vertice not in self.adj: 
            self.adj[id_vertice] = {} # Inicializa a lista de adjacência do vértice
            self.nodes_info[id_vertice] = info # Salva as informações extras

    def adicionar_aresta(self, origem, destino, peso):
        """
        Estabelece uma conexão bidirecional entre dois vértices com um peso definido.
        """
        if origem in self.adj and destino in self.adj:
            self.adj[origem][destino] = float(peso) 
            self.adj[destino][origem] = float(peso)

