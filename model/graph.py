from .vertex import Vertex
from .edge import Edge

class Graph:
    """Clase que gestiona la colección de vértices y aristas."""
    def __init__(self):
        self.vertices = {}  # Acceso rápido a vértices por ID
        self.edges = set()

    def add_vertex(self, id, role):
        """Añade un vértice al grafo si no existe."""
        if id not in self.vertices:
            self.vertices[id] = Vertex(id, role)
        return self.vertices[id]

    def get_vertex(self, id):
        """Obtiene un vértice por su ID."""
        return self.vertices.get(id)

    def add_edge(self, u_id, v_id, weight):
        """Añade una arista no dirigida entre dos vértices."""
        if u_id in self.vertices and v_id in self.vertices:
            u = self.vertices[u_id]
            v = self.vertices[v_id]
            # Añade la conexión en ambas direcciones
            u.add_neighbor(v, weight)
            v.add_neighbor(u, weight)
            self.edges.add(Edge(u, v, weight))

    def get_vertices_by_role(self, role):
        """Filtra y devuelve vértices según su rol."""
        return [v for v in self.vertices.values() if v.role == role]

    def has_edge(self, u_id, v_id):
        """Verifica si ya existe una arista entre dos nodos."""
        u = self.get_vertex(u_id)
        v = self.get_vertex(v_id)
        return v in u.neighbors if u and v else False

    def kruskal_mst(self):
        """
        Calcula el Árbol de Expansión Mínima (MST) usando el algoritmo de Kruskal.

        Returns:
            list: Una lista de tuplas, donde cada tupla representa una arista (u, v, peso) en el MST.
        """
        # Crear una lista de todas las aristas en el formato (peso, u_id, v_id)
        edges = []
        seen = set()
        for edge in self.edges:
            u_id = edge.u.id
            v_id = edge.v.id
            # Evitar duplicados en grafo no dirigido
            if (v_id, u_id) not in seen:
                edges.append((edge.weight, u_id, v_id))
                seen.add((u_id, v_id))

        # Ordenar las aristas por peso en orden ascendente
        edges.sort()

        parent = {vertex_id: vertex_id for vertex_id in self.vertices}
        mst_edges = []

        def find_set(v):
            if v == parent[v]:
                return v
            parent[v] = find_set(parent[v])
            return parent[v]

        def union_sets(a, b):
            a = find_set(a)
            b = find_set(b)
            if a != b:
                parent[b] = a

        for weight, u, v in edges:
            if find_set(u) != find_set(v):
                union_sets(u, v)
                mst_edges.append((u, v, weight))
                # Si el MST está completo (V-1 aristas), podemos parar.
                if len(mst_edges) == len(self.vertices) - 1:
                    break

        print(f"MST calculado con Kruskal. Total de aristas: {len(mst_edges)}")
        return mst_edges
    


