import streamlit as st
from sim.simulation import Simulation
from visual.dashboard import main_dashboard

# Inicializar el estado de la sesión si no existe
if 'simulation' not in st.session_state:
    # Creamos una instancia vacía que el dashboard llenará
    st.session_state.simulation = Simulation()

# Llamar a la función principal del dashboard, pasándole la simulación
if __name__ == "__main__":
    main_dashboard(st.session_state.simulation)