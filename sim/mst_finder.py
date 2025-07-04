# sim/mst_finder.py

class DisjointSet:
    """
    Una estructura de datos (Union-Find) para ayudar al algoritmo de Kruskal
    a detectar ciclos de manera eficiente.
    """
    def __init__(self, vertices):
        self.parent = {v.id: v.id for v in vertices}
        self.rank = {v.id: 0 for v in vertices}

    def find(self, i):
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            if self.rank[root_i] > self.rank[root_j]:
                self.parent[root_j] = root_i
            else:
                self.parent[root_i] = root_j
                if self.rank[root_i] == self.rank[root_j]:
                    self.rank[root_j] += 1
            return True
        return False

class MSTFinder:
    """
    Calcula el Árbol de Expansión Mínima (MST) usando el algoritmo de Kruskal.
    """
    def __init__(self, graph):
        self.graph = graph

    def find_mst(self):
        # 1. Crear una lista de todas las aristas y ordenarlas por peso (de menor a mayor)
        edges = sorted(self.graph.edges, key=lambda edge: edge.weight)
        
        # 2. Inicializar el conjunto para el Árbol de Expansión Mínima (MST)
        mst = []
        
        # 3. Crear una estructura DisjointSet para llevar el control de los subárboles
        ds = DisjointSet(self.graph.vertices.values())
        
        # 4. Iterar sobre las aristas ordenadas
        for edge in edges:
            u = edge.origin
            v = edge.destination
            
            # Si añadir esta arista no forma un ciclo...
            if ds.union(u.id, v.id):
                # ...la añadimos al MST
                mst.append(edge)
        
        return mst