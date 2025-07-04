# sim/simulation_initializer.py
import random
from model.graph import Graph

class SimulationInitializer:
    """Inicializa el entorno de la simulación, creando un grafo conexo."""
    def generate_graph(self, n_nodes, m_edges):
        graph = Graph()
        # Asignar roles (20% almacenamiento, 20% recarga, 60% clientes) [cite: 31, 32, 33]
        num_storage = max(1, int(n_nodes * 0.2))
        num_recharge = max(1, int(n_nodes * 0.2))
        num_clients = n_nodes - num_storage - num_recharge
        roles = ['storage'] * num_storage + ['recharge'] * num_recharge + ['client'] * num_clients
        random.shuffle(roles)
        
        # Coordenadas de Temuco como centro para el mapa
        temuco_coords = (-38.7359, -72.5904)

        # Crear vértices con coordenadas aleatorias alrededor de Temuco
        for i in range(n_nodes):
            lat = temuco_coords[0] + random.uniform(-0.05, 0.05)
            lon = temuco_coords[1] + random.uniform(-0.05, 0.05)
            graph.add_vertex(f"N{i}", roles[i], lat, lon)

        # 1. Asegurar conectividad para cumplir con la pauta [cite: 37]
        vertices = list(graph.vertices.values())
        random.shuffle(vertices)
        for i in range(n_nodes - 1):
            weight = random.randint(5, 20)
            graph.add_edge(vertices[i].id, vertices[i+1].id, weight)
        
        # 2. Añadir aristas aleatorias restantes
        max_possible_edges = n_nodes * (n_nodes - 1) // 2
        m_edges = min(m_edges, max_possible_edges)
        while len(graph.edges) < m_edges:
            u, v = random.sample(list(graph.vertices.keys()), 2)
            if not graph.has_edge(u, v):
                weight = random.randint(5, 30)
                graph.add_edge(u, v, weight)
        return graph