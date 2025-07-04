from fastapi import APIRouter, HTTPException
from sim.simulation import Simulation  # <-- Se importa la clase correcta
from collections import Counter

router = APIRouter()

# Variable global para mantener la instancia de la simulación
simulation: Simulation = None

def set_simulation(sim: Simulation):
    """
    Función para inyectar la instancia de la simulación desde main.py.
    """
    global simulation
    simulation = sim

def get_node_visit_ranking(sim: Simulation, role: str):
    """
    Obtiene un ranking de nodos visitados según su rol.
    """
    if not sim.graph:
        raise HTTPException(status_code=404, detail="La simulación no está activa.")
    
    # Filtra las órdenes que han sido completadas
    completed_orders = [o for o in sim.orders if o.status == 'Completed']
    if not completed_orders:
        return []

    # Cuenta las visitas a cada nodo de destino
    destination_counts = Counter(o.destination for o in completed_orders)
    
    ranking = []
    for node_id, visits in destination_counts.items():
        vertex = sim.graph.get_vertex(node_id)
        # Asegura que el nodo exista y tenga el rol correcto
        if vertex and vertex.role == role:
            ranking.append({"node_id": node_id, "visits": visits})
            
    return sorted(ranking, key=lambda x: x['visits'], reverse=True)

@router.get("/reports/visits/clients")
def get_most_visited_clients():
    if not simulation:
        raise HTTPException(status_code=503, detail="Simulación no disponible.")
    return get_node_visit_ranking(simulation, "Cliente")

@router.get("/reports/visits/recharges")
def get_most_visited_recharge_stations():
    if not simulation:
        raise HTTPException(status_code=503, detail="Simulación no disponible.")
    return get_node_visit_ranking(simulation, "Recarga")

@router.get("/reports/visits/storages")
def get_most_visited_storages():
    if not simulation:
        raise HTTPException(status_code=503, detail="Simulación no disponible.")
    
    completed_orders = [o for o in simulation.orders if o.status == 'Completed']
    if not completed_orders:
        return []
        
    origin_counts = Counter(o.origin for o in completed_orders)
    return [{"node_id": node_id, "visits": visits} for node_id, visits in origin_counts.items()]

@router.get("/reports/summary")
def get_simulation_summary():
    if not simulation:
        raise HTTPException(status_code=503, detail="Simulación no disponible.")
    
    return {
        "nodes_count": len(simulation.graph.vertices),
        "edges_count": len(simulation.graph.edges),
        "clients_count": len(simulation.clients),
        "orders_summary": {
            "total": len(simulation.orders),
            "pending": len([o for o in simulation.orders if o.status == 'Pending']),
            "completed": len([o for o in simulation.orders if o.status == 'Completed']),
            "cancelled": len([o for o in simulation.orders if o.status == 'Cancelled'])
        },
        "routes_logged_in_avl": len(simulation.get_frequent_routes())
    }