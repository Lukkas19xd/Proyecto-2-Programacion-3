# api/controllers/order_routes.py
# api/controllers/order_routes.py
from fastapi import APIRouter, HTTPException
from sim.simulation import Simulation

router = APIRouter()
# Asumimos que la simulación se pasa o está disponible globalmente
# En una aplicación real, esto podría manejarse con inyección de dependencias
simulation: Simulation = None 

def set_simulation(sim: Simulation):
    global simulation
    simulation = sim

@router.get("/orders/")
def get_all_orders():
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulación no iniciada.")
    return [order.to_dict() for order in simulation.get_orders()]

@router.get("/orders/{order_id}")
def get_order_by_id(order_id: str):
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulación no iniciada.")
    order = simulation.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada.")
    return order.to_dict()

@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: str):
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulación no iniciada.")
    if simulation.cancel_order(order_id):
        return {"message": "Orden cancelada con éxito."}
    raise HTTPException(status_code=400, detail="No se pudo cancelar la orden.")

@router.post("/orders/{order_id}/complete")
def complete_order(order_id: str):
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulación no iniciada.")
    if simulation.complete_order(order_id):
        return {"message": "Orden completada con éxito."}
    raise HTTPException(status_code=400, detail="No se pudo completar la orden.")