# api/main.py
# api/main.py
# api/main.py
# api/main.py
import random
from fastapi import FastAPI, Depends
from sim.simulation import Simulation
from domain.client import Client
from domain.order import Order
from .depedencies import get_simulation

# --- Importamos todos los routers ---
from .controllers import client_routes, order_routes, report_routes, info_routes

# Inicializa la aplicación FastAPI
app = FastAPI(
    title="API del Sistema Logístico de Drones",
    description="API para interactuar con la simulación de la red de drones de Correos Chile.",
    version="1.0.0"
)

# --- Incluimos todos los routers en la aplicación principal ---
app.include_router(client_routes.router)
app.include_router(order_routes.router)
app.include_router(report_routes.router)
app.include_router(info_routes.router)


@app.get("/", tags=["Root"])
def read_root():
    """
    Endpoint principal que da la bienvenida a la API.
    """
    return {"message": "Bienvenido a la API del Sistema Logístico de Drones"}

@app.post("/simulation/run", tags=["Simulation"])
def run_simulation(n_nodes: int = 15, m_edges: int = 20, n_orders: int = 10, sim: Simulation = Depends(get_simulation)):
    """
    Inicia o reinicia la simulación con nuevos parámetros.
    Este endpoint simula el botón "Iniciar Simulación" del dashboard.
    """
    sim.__init__()  # Resetea la simulación
    sim.graph = sim.initializer.generate_graph(n_nodes, m_edges)
    
    client_nodes = [v for v in sim.graph.vertices.values() if v.role == "client"]
    storage_nodes = [v for v in sim.graph.vertices.values() if v.role == "storage"]
    
    for node in client_nodes:
        sim.clients.insert(node.id, Client(node.id, f"Cliente_{node.id}"))
    
    if client_nodes and storage_nodes:
        for _ in range(n_orders):
            client = random.choice(client_nodes)
            storage = random.choice(storage_nodes)
            order_id = sim.order_counter
            sim.orders.insert(order_id, Order(order_id, client.id, storage.id, client.id))
            sim.order_counter += 1
            
    return {"status": "success", "message": f"Simulación generada con {n_nodes} nodos, {m_edges} aristas y {n_orders} órdenes."}