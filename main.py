# main.py (en la carpeta raíz del proyecto)

import streamlit as st
import uvicorn
import threading
import time
from sim.simulation import Simulation
from visual.dashboard import main_dashboard # Importamos la función del dashboard

# --- Función para ejecutar la API de FastAPI en segundo plano ---
def run_api():
    """Ejecuta la API de FastAPI usando uvicorn en un hilo separado."""
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, log_level="info")

# --- Lógica principal de la aplicación ---

# Usamos st.session_state para que la simulación y el hilo no se reinicien en cada acción
if 'simulation' not in st.session_state:
    st.session_state.simulation = Simulation()

if 'api_thread_started' not in st.session_state:
    st.session_state.api_thread_started = False

# Iniciar el hilo de la API solo una vez al arrancar la app
if not st.session_state.api_thread_started:
    st.info("Iniciando el servidor de la API en segundo plano...")
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    time.sleep(2) # Damos un momento para que el servidor levante
    st.session_state.api_thread_started = True
    st.rerun() # Recargamos para limpiar el mensaje de inicio

# --- Ejecutar el Dashboard Principal ---
# Llamamos a la función que construye toda la interfaz de Streamlit
main_dashboard(st.session_state.simulation)