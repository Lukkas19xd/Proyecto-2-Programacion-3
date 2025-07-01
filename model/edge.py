class Edge:
    """Representa una arista o conexión entre dos vértices."""
    def __init__(self, origin, destination, weight):
        self.origin = origin
        self.destination = destination
        self.weight = weight  # Costo o distancia de la arista

    def __repr__(self):
        """Representación en string de la arista."""
        return f"Edge({self.origin.id} -> {self.destination.id}, W:{self.weight})"