from fastapi import FastAPI, HTTPException
# Asegúrate de que la ruta de importación sea correcta desde la raíz de tu proyecto
from sim.simulation import Simulation 
from .controllers import client_routes, order_routes, report_routes, info_routes

# --- Creación de la Aplicación FastAPI ---
app = FastAPI(
    title="API del Sistema Logístico de Drones",
    description="API para consultar y gestionar la simulación de la red de drones.",
    version="1.0.0"
)

# --- Instancia de la Simulación ---
# Se crea una única instancia de la simulación para que toda la API la utilice.
try:
    simulation_instance = Simulation(n_nodes=50, m_edges=70, n_orders=30)
except Exception as e:
    raise RuntimeError(f"No se pudo inicializar la simulación: {e}") from e

# --- Inyectar la simulación en los controladores ---
# Es crucial que cada controlador sepa con qué instancia de la simulación trabajar.
# La función set_simulation (que debes crear en cada archivo de rutas) se encarga de esto.
client_routes.set_simulation(simulation_instance)
order_routes.set_simulation(simulation_instance)
report_routes.set_simulation(simulation_instance)
info_routes.set_simulation(simulation_instance)


# --- Registrar los Routers en la Aplicación Principal ---
# Agregamos todos los grupos de endpoints a la aplicación principal.
app.include_router(client_routes.router, prefix="/api", tags=["Clients"])
app.include_router(order_routes.router, prefix="/api", tags=["Orders"])
app.include_router(report_routes.router, prefix="/api", tags=["Reports"])
app.include_router(info_routes.router, prefix="/api", tags=["Info"])


# --- Endpoint Raíz ---
@app.get("/", tags=["Root"])
def read_root():
    """
    Endpoint principal que da la bienvenida a la API.
    """
    return {"message": "Bienvenido a la API del Sistema Logístico de Drones"}