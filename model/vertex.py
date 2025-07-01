class Vertex:
    """Representa un nodo en el grafo (cliente, almacén o estación)."""
    def __init__(self, id, role):
        self.id = id
        self.role = role
        self.neighbors = {}  # Clave: objeto Vertex del vecino, Valor: peso de la arista

    def add_neighbor(self, neighbor, weight):
        """Añade un vecino a este vértice."""
        self.neighbors[neighbor] = weight

    def __repr__(self):
        """Representación en string del vértice."""
        return f"Vertex({self.id}, '{self.role}')"
    
    def __lt__(self, other):
        """Permite comparar vértices para estructuras como colas de prioridad."""
        return self.id < other.id