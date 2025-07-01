# api/controllers/info_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sim.simulation import Simulation
from ..depedencies import get_simulation
from collections import Counter

router = APIRouter(
    prefix="/info",
    tags=["Info & Statistics"]
)

def get_node_visit_ranking(sim: Simulation, role: str):
    """
    Función auxiliar para obtener el ranking de visitas de nodos por un rol específico.
    """
    if not sim.graph:
        raise HTTPException(status_code=404, detail="La simulación no está activa.")

    # Filtra las órdenes entregadas para obtener los destinos
    delivered_orders = [o for o in sim.orders.values() if o.status == 'Delivered']
    if not delivered_orders:
        return []

    # Cuenta la frecuencia de cada destino
    destination_counts = Counter(o.destination for o in delivered_orders)
    
    # Filtra los nodos por el rol solicitado y crea el ranking
    ranking = []
    for node_id, visits in destination_counts.items():
        vertex = sim.graph.get_vertex(node_id)
        if vertex and vertex.role == role:
            ranking.append({"node_id": node_id, "visits": visits})
            
    # Ordena el ranking de mayor a menor número de visitas
    return sorted(ranking, key=lambda x: x['visits'], reverse=True)


@router.get("/reports/visits/clients")
def get_most_visited_clients(sim: Simulation = Depends(get_simulation)):
    """
    Obtiene el ranking de clientes más visitados en las rutas de la simulación.
    """
    return get_node_visit_ranking(sim, "client")

@router.get("/reports/visits/recharges")
def get_most_visited_recharge_stations(sim: Simulation = Depends(get_simulation)):
    """
    Obtiene el ranking de nodos de recarga más visitados.
    Nota: Esta es una simplificación. Un conteo real requeriría registrar cada parada.
    Por ahora, se basa en si un nodo de recarga fue un destino final.
    """
    return get_node_visit_ranking(sim, "recharge")

@router.get("/reports/visits/storages")
def get_most_visited_storages(sim: Simulation = Depends(get_simulation)):
    """
    Obtiene el ranking de nodos de almacenamiento más visitados como origen.
    Nota: La lógica actual se basa en destinos. Una implementación completa
    debería contar los orígenes de las rutas.
    """
    # Simplificación: Adaptamos la lógica para contar orígenes
    if not sim.graph:
        raise HTTPException(status_code=404, detail="La simulación no está activa.")
        
    delivered_orders = [o for o in sim.orders.values() if o.status == 'Delivered']
    if not delivered_orders:
        return []

    origin_counts = Counter(o.origin for o in delivered_orders)
    return [{"node_id": node_id, "visits": visits} for node_id, visits in origin_counts.items()]


@router.get("/reports/summary")
def get_simulation_summary(sim: Simulation = Depends(get_simulation)):
    """
    Obtiene un resumen general de la simulación activa.
    """
    if not sim.graph:
        raise HTTPException(status_code=404, detail="La simulación no está activa.")

    total_orders = len(sim.orders.values())
    delivered_count = len([o for o in sim.orders.values() if o.status == 'Delivered'])
    
    return {
        "nodes_count": len(sim.graph.vertices),
        "edges_count": len(sim.graph.edges),
        "clients_count": len(sim.clients.values()),
        "orders_summary": {
            "total": total_orders,
            "pending": len([o for o in sim.orders.values() if o.status == 'Pending']),
            "delivered": delivered_count,
            "cancelled": len([o for o in sim.orders.values() if o.status == 'Cancelled'])
        },
        "routes_logged_in_avl": len(sim.avl.get_frequent_routes())
    }