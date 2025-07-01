# api/controllers/order_routes.py
# api/controllers/order_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sim.simulation import Simulation
from sim.pathfinder import Pathfinder
from ..dependencias import get_simulation

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

@router.get("/")
def get_all_orders(sim: Simulation = Depends(get_simulation)):
    """
    [cite_start]Lista todas las órdenes registradas en el sistema. [cite: 206]
    """
    if not sim.orders:
        raise HTTPException(status_code=404, detail="No hay órdenes en la simulación activa.")
    
    order_list = [order.to_dict() for order in sim.orders.values()]
    return order_list

@router.get("/{order_id}")
def get_order_by_id(order_id: int, sim: Simulation = Depends(get_simulation)):
    """
    [cite_start]Obtiene el detalle de una orden específica por su ID. [cite: 213]
    """
    order = sim.orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Orden con ID '{order_id}' no encontrada.")
    return order.to_dict()

@router.post("/{order_id}/complete")
def complete_order(order_id: int, sim: Simulation = Depends(get_simulation)):
    """
    [cite_start]Marca una orden específica como completada. [cite: 229]
    Esto implica encontrar una ruta y simular la entrega.
    """
    order = sim.orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Orden con ID '{order_id}' no encontrada.")
    
    if order.status != "Pending":
        raise HTTPException(status_code=400, detail=f"La orden {order_id} no está pendiente, su estado es '{order.status}'.")

    # Usamos el Pathfinder para encontrar la ruta y el costo
    pathfinder = Pathfinder(sim.graph)
    path, cost = pathfinder.find_path(order.origin, order.destination)

    if path:
        order.deliver(cost)
        sim.clients.get(order.client_id).increment_orders()
        sim.avl.add_route(path)
        return {"message": f"Orden {order_id} completada con éxito.", "path": [v.id for v in path], "cost": cost}
    else:
        raise HTTPException(status_code=400, detail=f"No se encontró una ruta viable para la orden {order_id}.")

@router.post("/{order_id}/cancel")
def cancel_order(order_id: int, sim: Simulation = Depends(get_simulation)):
    """
    [cite_start]Cancela una orden específica. [cite: 220]
    """
    order = sim.orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Orden con ID '{order_id}' no encontrada.")
    
    if order.cancel():
        return {"message": f"Orden {order_id} ha sido cancelada."}
    else:
        raise HTTPException(status_code=400, detail=f"No se pudo cancelar la orden {order_id}. Su estado actual es '{order.status}'.")