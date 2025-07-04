from fastapi import APIRouter, HTTPException
from sim.simulation import Simulation

router = APIRouter()

# Variable global para mantener la instancia de la simulación
simulation: Simulation = None

def set_simulation(sim: Simulation):
    """
    Esta es la función que faltaba.
    Permite que main.py inyecte la instancia de la simulación.
    """
    global simulation
    simulation = sim

@router.get("/clients/")
def get_all_clients():
    """Obtiene la lista completa de clientes registrados."""
    if not simulation or not simulation.clients:
        raise HTTPException(status_code=404, detail="No hay clientes o la simulación no está activa.")
    # Suponiendo que self.clients es un diccionario de objetos Client
    return [client.to_dict() for client in simulation.clients.values()]

@router.get("/clients/{client_id}")
def get_client_by_id(client_id: str):
    """Obtiene la información detallada de un cliente por su ID."""
    if not simulation or not simulation.clients:
        raise HTTPException(status_code=404, detail="Simulación no activa.")
    
    client = simulation.clients.get(client_id)
    if not client:
        raise HTTPException(status_code=404, detail=f"Cliente con ID '{client_id}' no encontrado.")
    return client.to_dict()