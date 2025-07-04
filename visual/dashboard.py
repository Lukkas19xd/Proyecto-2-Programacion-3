# visual/dashboard.py

import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from visual.map.map_builder import MapBuilder
from visual.avl_visualizer import AVLVisualizer
from visual.report_generator import generate_pdf_report
from sim.simulation import Simulation

# --- Funciones para cada pestaña, replicando el video ---

def show_run_simulation(simulation: Simulation):
    st.header("1. Configure Simulation Parameters")
    with st.container(border=True):
        n_nodes = st.slider("Number of Nodes", 10, 150, st.session_state.get('n_nodes', 15))
        min_edges = n_nodes - 1
        m_edges = st.slider("Number of Edges", min_edges, 300, max(min_edges, st.session_state.get('m_edges', 20)))
        n_orders = st.slider("Number of Orders", 10, 300, st.session_state.get('n_orders', 10))

        st.session_state.update(n_nodes=n_nodes, m_edges=m_edges, n_orders=n_orders)

        if st.button("🚀 Start Simulation", use_container_width=True):
            with st.spinner('Generating network...'):
                simulation.start_new_simulation(n_nodes, m_edges, n_orders)
            st.rerun()

def show_explore_network(simulation: Simulation):
    st.header("2. Explore Network")
    if not simulation.graph:
        st.warning("Please start a simulation first.")
        return

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            origin_nodes = [v.vertex_id for v in simulation.get_nodes_by_role("Warehouses")]
            selected_origin = st.selectbox("Select Origin (Warehouse)", options=origin_nodes)
        with col2:
            destination_nodes = [v.vertex_id for v in simulation.get_nodes_by_role("Clients")]
            selected_destination = st.selectbox("Select Destination (Client)", options=destination_nodes)

        algorithm = st.radio("Pathfinding Algorithm", ["Dijkstra", "Floyd-Warshall"], horizontal=True)

        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            if st.button("Calculate Route", use_container_width=True):
                path, cost = simulation.find_path(selected_origin, selected_destination, algorithm)
                st.session_state.update(calculated_path=path, path_cost=cost, show_mst=False)
                st.rerun()
        with btn_col2:
            if st.button("Complete & Create Order", use_container_width=True, disabled=not st.session_state.get('calculated_path')):
                simulation.create_order_from_route(selected_origin, selected_destination, st.session_state.calculated_path, st.session_state.path_cost)
                st.success(f"Order created for route {selected_origin} -> {selected_destination}")
                st.session_state.calculated_path = None
                st.rerun()
        with btn_col3:
            if st.button("Show/Hide MST", use_container_width=True):
                st.session_state.show_mst = not st.session_state.get('show_mst', False)
                if st.session_state.show_mst:
                    st.session_state.mst_edges = simulation.get_mst()
                st.rerun()

    if st.session_state.get('calculated_path'):
        st.subheader("Flight Summary")
        st.info(f"Route: `{' -> '.join(st.session_state.calculated_path)}` | Cost: `{st.session_state.path_cost}`")

    MapBuilder(simulation)

def show_clients_and_orders(simulation: Simulation):
    st.header("3. Clients & Orders")
    if not simulation.graph:
        st.warning("Please start a simulation first.")
        return
    
    st.subheader("Client List")
    st.json([client.to_dict() for client in simulation.get_all_clients()])
    
    st.subheader("Order List")
    st.json([order.to_dict() for order in simulation.get_all_orders()])

def show_route_analytics(simulation: Simulation):
    st.header("4. Route Analytics")
    if not simulation.route_avl or simulation.route_avl.is_empty():
        st.warning("No routes recorded yet. Complete deliveries to see analytics.")
        return

    st.subheader("Most Frequent Routes (AVL Tree)")
    fig = visualize_avl_tree(simulation.route_avl)
    if fig:
        st.pyplot(fig)

    st.subheader("Export System Report")
    if st.button("Generate PDF Report", use_container_width=True):
        with st.spinner("Generating PDF..."):
            pdf_data = generate_pdf_report(simulation)
            st.download_button("Download PDF", pdf_data, "simulation_report.pdf", "application/pdf", use_container_width=True)

def show_general_statistics(simulation: Simulation):
    st.header("5. General Statistics")
    if not simulation.graph:
        st.warning("Please start a simulation first.")
        return

    st.subheader("Node Distribution by Role")
    roles = [v.role for v in simulation.graph.get_vertices()]
    if roles:
        role_counts = {role: roles.count(role) for role in set(roles)}
        fig1, ax1 = plt.subplots()
        ax1.pie(role_counts.values(), labels=role_counts.keys(), autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1)

    st.subheader("Most Visited Nodes Comparison")
    try:
        API_URL = "http://127.0.0.1:8000"
        clients_resp = requests.get(f"{API_URL}/info/reports/visits/clients").json()
        recharges_resp = requests.get(f"{API_URL}/info/reports/visits/recharges").json()
        storages_resp = requests.get(f"{API_URL}/info/reports/visits/storages").json()

        data = {
            "Clients": sum(item['visits'] for item in clients_resp),
            "Recharge": sum(item['visits'] for item in recharges_resp),
            "Storage": sum(item['visits'] for item in storages_resp)
        }
        
        fig2, ax2 = plt.subplots()
        ax2.bar(data.keys(), data.values(), color=['green', 'blue', 'orange'])
        ax2.set_ylabel('Total Visits')
        ax2.set_title('Total Visits by Node Role')
        st.pyplot(fig2)
    except requests.exceptions.ConnectionError:
        st.error("API connection failed. Ensure the server is running correctly.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# --- Función principal que construye el dashboard ---
def main_dashboard(simulation: Simulation):
    st.set_page_config(page_title="Drone Logistics Simulation", layout="wide")
    st.title("🚁 Drone Logistics Simulation - Correos Chile")

    tabs = ["Run Simulation", "Explore Network", "Clients & Orders", "Route Analytics", "General Statistics"]
    tab1, tab2, tab3, tab4, tab5 = st.tabs(tabs)

    with tab1:
        show_run_simulation(simulation)
    with tab2:
        show_explore_network(simulation)
    with tab3:
        show_clients_and_orders(simulation)
    with tab4:
        show_route_analytics(simulation)
    with tab5:
        show_general_statistics(simulation)