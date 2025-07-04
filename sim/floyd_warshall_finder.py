# sim/floyd_warshall_finder.py
import itertools

class FloydWarshallFinder:
    """
    Calcula y almacena las rutas más cortas entre todos los pares de nodos
    utilizando el algoritmo de Floyd-Warshall.
    """
    def __init__(self, graph):
        self.nodes = list(graph.vertices.values())
        self.node_map = {node.id: i for i, node in enumerate(self.nodes)}
        self.num_nodes = len(self.nodes)
        
        # Inicializar matrices de distancia y sucesores
        self.dist = [[float('inf')] * self.num_nodes for _ in range(self.num_nodes)]
        self.next_node = [[None] * self.num_nodes for _ in range(self.num_nodes)]

        self._initialize_matrices(graph)
        self._calculate_all_pairs_shortest_paths()

    def _initialize_matrices(self, graph):
        """Prepara las matrices con los datos iniciales del grafo."""
        for i in range(self.num_nodes):
            self.dist[i][i] = 0

        for edge in graph.edges:
            u_idx = self.node_map[edge.origin.id]
            v_idx = self.node_map[edge.destination.id]
            
            # Para grafos no dirigidos, la arista va en ambas direcciones
            self.dist[u_idx][v_idx] = edge.weight
            self.dist[v_idx][u_idx] = edge.weight
            self.next_node[u_idx][v_idx] = v_idx
            self.next_node[v_idx][u_idx] = u_idx

    def _calculate_all_pairs_shortest_paths(self):
        """Ejecuta el algoritmo principal de Floyd-Warshall."""
        for k, i, j in itertools.product(range(self.num_nodes), repeat=3):
            # Si encontramos una ruta más corta a través del nodo k...
            if self.dist[i][j] > self.dist[i][k] + self.dist[k][j]:
                # ...actualizamos la distancia y el siguiente nodo en la ruta.
                self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
                self.next_node[i][j] = self.next_node[i][k]

    def get_path(self, start_id, end_id):
        """
        Reconstruye la ruta más corta entre dos nodos usando la matriz de sucesores.
        """
        if start_id not in self.node_map or end_id not in self.node_map:
            return None, float('inf')

        u_idx = self.node_map[start_id]
        v_idx = self.node_map[end_id]

        if self.next_node[u_idx][v_idx] is None:
            return None, float('inf') # No hay ruta

        path_indices = [u_idx]
        current_idx = u_idx
        while current_idx != v_idx:
            current_idx = self.next_node[current_idx][v_idx]
            if current_idx is None: return None, float('inf') # Ruta interrumpida
            path_indices.append(current_idx)
        
        # Convertir los índices de la ruta de vuelta a objetos Vertex
        path_nodes = [self.nodes[i] for i in path_indices]
        cost = self.dist[u_idx][v_idx]
        
        return path_nodes, cost