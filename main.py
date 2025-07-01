# streamlit run main.py
import streamlit as st
from sim.simulation import Simulation

st.set_page_config(page_title="Sistema Logístico de Drones", layout="wide")

# Usar st.session_state para que la simulación no se reinicie en cada acción
if 'simulation' not in st.session_state:
    st.session_state.simulation = Simulation()

st.session_state.simulation.run_dashboard()