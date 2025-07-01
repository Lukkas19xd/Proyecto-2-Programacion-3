# api/controllers/client_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sim.simulation import Simulation
from ..dependencias import get_simulation

# El router es como un "mini-FastAPI" que podemos incluir en la aplicación principal.
router = APIRouter(
    prefix="/clients",  # Todas las rutas en este archivo comenzarán con /clients
    tags=["Clients"]    # Agrupa estos endpoints en la documentación de la API
)

@router.get("/")
def get_all_clients(sim: Simulation = Depends(get_simulation)):
    """
    Obtiene la lista completa de clientes registrados en el sistema.
    Utiliza el método .values() de tu HashMap para obtener todos los clientes.
    """
    if not sim.clients:
        raise HTTPException(status_code=404, detail="No hay clientes en la simulación activa.")
    
    # Convierte cada objeto Cliente a su representación de diccionario
    client_list = [client.to_dict() for client in sim.clients.values()]
    return client_list

@router.get("/{client_id}")
def get_client_by_id(client_id: str, sim: Simulation = Depends(get_simulation)):
    """
    Obtiene la información detallada de un cliente específico por su ID.
    """
    client = sim.clients.get(client_id)
    
    if client is None:
        # Si el cliente no se encuentra, devuelve un error 404
        raise HTTPException(status_code=404, detail=f"Cliente con ID '{client_id}' no encontrado.")
        
    return client.to_dict()