# api/dependencies.py
from sim.simulation import Simulation

# Creamos una instancia única de la simulación que será compartida.
simulation = Simulation()

def get_simulation():
    """
    Retorna la instancia compartida de la simulación.
    Esto asegura que todos los endpoints de la API usen el mismo objeto de simulación.
    """
    return simulation