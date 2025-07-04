import math

class FloydWarshallFinder:
    """
    Calcula y almacena las rutas más cortas entre todos los pares de nodos
    utilizando el algoritmo de Floyd-Warshall.
    """
    def __init__(self, graph):
        self.graph = graph
        self.dist = []      # Matriz de distancias
        self.next_node = [] # Matriz para reconstruir caminos
        self.node_map = {}  # Mapeo de ID de nodo a índice de matriz
        if graph:
            self._initialize_matrices(graph)
            self._calculate_paths()

    def _initialize_matrices(self, graph):
        """Prepara las matrices de distancia y de siguiente nodo."""
        nodes = list(graph.vertices.keys())
        self.node_map = {node_id: i for i, node_id in enumerate(nodes)}
        n = len(nodes)
        
        # Inicializar matrices con infinito y None
        self.dist = [[math.inf] * n for _ in range(n)]
        self.next_node = [[None] * n for _ in range(n)]

        # Establecer la distancia de un nodo a sí mismo como 0
        for i in range(n):
            self.dist[i][i] = 0

        # Poblar las matrices con las aristas existentes
        for edge in graph.edges:
            # **AQUÍ ESTÁ LA CORRECCIÓN FINAL**
            # Usamos edge.u y edge.v, que son los atributos correctos de la clase Edge
            u_idx = self.node_map.get(edge.u)
            v_idx = self.node_map.get(edge.v)
            
            if u_idx is not None and v_idx is not None:
                self.dist[u_idx][v_idx] = edge.weight
                self.dist[v_idx][u_idx] = edge.weight # Para grafos no dirigidos
                self.next_node[u_idx][v_idx] = v_idx
                self.next_node[v_idx][u_idx] = u_idx

    def _calculate_paths(self):
        """Ejecuta el algoritmo de Floyd-Warshall."""
        n = len(self.dist)
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if self.dist[i][k] + self.dist[k][j] < self.dist[i][j]:
                        self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
                        self.next_node[i][j] = self.next_node[i][k]

    def get_path(self, start_id: str, end_id: str):
        """Reconstruye y devuelve la ruta más corta y su costo."""
        if not self.dist:
            return None, math.inf

        start_idx = self.node_map.get(start_id)
        end_idx = self.node_map.get(end_id)

        if start_idx is None or end_idx is None or self.dist[start_idx][end_idx] == math.inf:
            return None, math.inf

        path_indices = []
        u, v = start_idx, end_idx
        while u != v:
            path_indices.append(u)
            u = self.next_node[u][v]
            if u is None: return None, math.inf # Ruta no encontrada
        path_indices.append(v)
        
        # Convertir índices de nuevo a IDs de nodos
        id_map = {i: node_id for node_id, i in self.node_map.items()}
        path_ids = [self.graph.get_vertex(id_map[i]) for i in path_indices]
        
        return path_ids, self.dist[start_idx][end_idx]