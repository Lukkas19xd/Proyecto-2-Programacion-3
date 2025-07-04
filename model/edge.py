# Archivo: model/edge.py
class Edge:
    """
    Representa una arista (conexión) en el grafo.
    """
    def __init__(self, u: str, v: str, weight: int):
        """
        Constructor de la arista.

        Args:
            u (str): El ID del nodo de inicio (ej: "N1").
            v (str): El ID del nodo de fin (ej: "N2").
            weight (int): El peso o costo de la arista.
        """
        # **ATRIBUTOS CORRECTOS Y DEFINITIVOS**
        self.u = u
        self.v = v
        self.weight = weight

    def __repr__(self):
        """Representación en string de la arista."""
        return f"Edge({self.u} -> {self.v}, w: {self.weight})"