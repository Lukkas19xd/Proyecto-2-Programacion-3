# Archivo: sim/pathfinder.py
import heapq
from collections import deque

class Pathfinder:
    """Encuentra la ruta óptima usando el algoritmo de Dijkstra, considerando la autonomía del dron."""
    def __init__(self, graph, battery_limit=50):
        self.graph = graph
        self.battery_limit = battery_limit

    def find_path(self, start_id, end_id):
        """
        Implementación del algoritmo de Dijkstra para encontrar el camino más corto.
        Utiliza una cola de prioridad para explorar siempre el nodo de menor costo.
        """
        start_node = self.graph.get_vertex(start_id)
        end_node = self.graph.get_vertex(end_id)
        if not start_node or not end_node:
            return None, float('inf')

        # Cola de prioridad: (costo_total, nodo_actual, ruta_hasta_ahora, bateria_restante)
        pq = [(0, start_node, [start_node], self.battery_limit)]
        
        # Diccionario para llevar el registro del costo mínimo para llegar a un nodo
        min_costs = {start_node.id: 0}

        while pq:
            cost, current_node, path, battery = heapq.heappop(pq)

            # Si llegamos al destino, hemos encontrado la ruta más corta
            if current_node.id == end_id:
                return path, cost

            # Si el costo actual es mayor que el mínimo ya registrado, ignoramos esta ruta
            if cost > min_costs.get(current_node.id, float('inf')):
                continue

            # Si estamos en una estación de recarga, la batería se restaura
            current_battery = self.battery_limit if current_node.role == 'recharge' else battery

            # Explorar vecinos
            for neighbor, weight in current_node.neighbors.items():
                # Solo continuamos si el dron tiene suficiente batería para el siguiente tramo
                if current_battery >= weight:
                    new_cost = cost + weight
                    
                    # Si encontramos una ruta más barata hacia el vecino, la actualizamos
                    if new_cost < min_costs.get(neighbor.id, float('inf')):
                        min_costs[neighbor.id] = new_cost
                        new_path = path + [neighbor]
                        new_battery = current_battery - weight
                        heapq.heappush(pq, (new_cost, neighbor, new_path, new_battery))

        return None, float('inf') # No se encontró una ruta viable