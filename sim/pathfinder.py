# Archivo: sim/pathfinder.py
from collections import deque

class Pathfinder:
    """Encuentra rutas usando BFS, considerando la autonomía del dron."""
    def __init__(self, graph, battery_limit=50):
        self.graph = graph
        self.battery_limit = battery_limit

    def find_path(self, start_id, end_id):
        start_node = self.graph.get_vertex(start_id)
        end_node = self.graph.get_vertex(end_id)
        if not start_node or not end_node: return None, float('inf')

        # Cola para BFS: (nodo_actual, ruta_hasta_ahora, costo_desde_ultima_carga)
        queue = deque([(start_node, [start_node], 0)])
        visited = {start_node.id}

        while queue:
            current_node, path, cost = queue.popleft()

            if current_node.id == end_id:
                # Calculamos el costo total real de la ruta encontrada
                total_cost = 0
                for i in range(len(path) - 1):
                    total_cost += path[i].neighbors[path[i+1]]
                return path, total_cost

            # Lógica de recarga: si estamos en una estación, el costo para el siguiente paso se resetea
            cost_from_here = 0 if current_node.role == 'recharge' else cost

            for neighbor, weight in current_node.neighbors.items():
                if neighbor not in visited:
                    new_cost = cost_from_here + weight
                    if new_cost <= self.battery_limit:
                        visited.add(neighbor)
                        new_path = path + [neighbor]
                        queue.append((neighbor, new_path, new_cost))

        return None, float('inf') # No se encontró ruta