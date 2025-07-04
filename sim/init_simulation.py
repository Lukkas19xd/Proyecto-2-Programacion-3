# Archivo: sim/init_simulation.py
import random
from model.graph import Graph
from model.vertex import Vertex

def create_connected_graph(n_nodes: int, m_edges: int) -> Graph:
    """
    Crea un grafo conectado y geolocalizado con roles asignados a los nodos.

    Args:
        n_nodes (int): El número de nodos en el grafo.
        m_edges (int): El número de aristas en el grafo.

    Returns:
        Graph: Un objeto Graph conectado.
    """
    g = Graph()
    
    # 1. Crear Nodos con Coordenadas Aleatorias (simulando Temuco)
    # Coordenadas aproximadas del área de Temuco
    lat_range = (-38.75, -38.70)
    lon_range = (-72.65, -72.55)
    
    for i in range(n_nodes):
        lat = random.uniform(*lat_range)
        lon = random.uniform(*lon_range)
        g.add_vertex(Vertex(f"N{i+1}", lat, lon))

    # 2. Asignar Roles a los Nodos
    nodes = list(g.vertices.values())
    random.shuffle(nodes)
    
    num_storage = int(n_nodes * 0.20)
    num_recharge = int(n_nodes * 0.20)
    
    for i, node in enumerate(nodes):
        if i < num_storage:
            node.role = "Almacenamiento"
        elif i < num_storage + num_recharge:
            node.role = "Recarga"
        else:
            node.role = "Cliente"

    # 3. Asegurar Conectividad Inicial (Creando un Árbol)
    all_nodes = list(g.vertices.keys())
    random.shuffle(all_nodes)
    
    for i in range(len(all_nodes) - 1):
        weight = random.randint(5, 20)
        g.add_edge(all_nodes[i], all_nodes[i+1], weight)

    # 4. Añadir Aristas Aleatorias Adicionales hasta llegar a m_edges
    edges_to_add = m_edges - (n_nodes - 1)
    
    while edges_to_add > 0 and len(g.edges) < n_nodes * (n_nodes - 1) // 2:
        u, v = random.sample(all_nodes, 2)
        # Asegurarse de no añadir aristas duplicadas
        if not g.get_edge(u, v):
            weight = random.randint(5, 50)
            g.add_edge(u, v, weight)
            edges_to_add -= 1
            
    return g