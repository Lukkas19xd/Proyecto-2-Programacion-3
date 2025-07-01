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