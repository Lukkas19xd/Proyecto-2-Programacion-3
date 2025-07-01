# Archivo: sim/simulation.py
import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
from collections import Counter
import random
import time

from sim.simulation_initializer import SimulationInitializer
from sim.pathfinder import Pathfinder
from domain.client import Client
from domain.order import Order
from tda.hashmap import HashMap
from tda.avl import AVLTree
from visual.avl_visualizer import AVLVisualizer
from visual.networkx_adapter import NetworkXAdapter

class Simulation:
    def __init__(self):
        self.graph = None
        self.initializer = SimulationInitializer()
        self.clients = HashMap()
        self.orders = HashMap()
        self.avl = AVLTree()
        self.order_counter = 1

    def run_dashboard(self):
        st.title("📦 Sistema Logístico Autónomo con Drones")
        tabs = st.tabs(["🔄 Simulación", "🌍 Explorar Red", "👤 Clientes y Órdenes", "📊 Analítica", "📈 Estadísticas"])
        
        with tabs[0]: self._run_simulation_tab()
        with tabs[1]: self._explore_network_tab()
        with tabs[2]: self._clients_orders_tab()
        with tabs[3]: self._route_analytics_tab()
        with tabs[4]: self._general_statistics_tab()

    def _run_simulation_tab(self):
        st.header("🔧 Configuración de la Simulación")
        n_nodes = st.slider("Número de Nodos", 10, 150, 15, key="n_nodes")
        m_edges = st.slider("Número de Aristas", n_nodes - 1, 300, 20, key="m_edges")
        n_orders = st.slider("Número de Órdenes", 1, 50, 10, key="n_orders")
        
        # Texto informativo
        st.info(f"Se crearán aproximadamente:\n- {int(n_nodes*0.2)} nodos de almacenamiento (20%)\n- {int(n_nodes*0.2)} nodos de recarga (20%)\n- {int(n_nodes*0.6)} nodos de cliente (60%)")

        if st.button("🚀 Iniciar Simulación"):
            self.__init__() # Resetea el estado
            with st.spinner('Generando grafo...'):
                self.graph = self.initializer.generate_graph(n_nodes, m_edges)
            
            # Crear Clientes y Órdenes
            client_nodes = self.graph.get_vertices_by_role("client")
            storage_nodes = self.graph.get_vertices_by_role("storage")
            for node in client_nodes: self.clients.insert(node.id, Client(node.id, f"Cliente_{node.id}"))
            
            if client_nodes and storage_nodes:
                for _ in range(n_orders):
                    client = random.choice(client_nodes)
                    storage = random.choice(storage_nodes)
                    self.orders.insert(self.order_counter, Order(self.order_counter, client.id, storage.id, client.id))
                    self.order_counter += 1
            st.success("¡Simulación generada!")

    def _explore_network_tab(self):
        st.header("🌍 Visualización y Procesamiento de Rutas")
        if not self.graph:
            st.warning("Primero debe iniciar una simulación."); return
        
        col1, col2 = st.columns([2, 1])
        with col1:
            adapter = NetworkXAdapter(self.graph)
            fig = adapter.draw(st.session_state.get('path_to_highlight'))
            st.pyplot(fig)
        
        with col2:
            st.subheader("Seleccionar Ruta")
            pending_orders = {f"Orden #{o.order_id} ({o.origin} -> {o.destination})": o for o in self.orders.values() if o.status == 'Pending'}
            if not pending_orders:
                st.success("¡No hay órdenes pendientes!")
                return
            
            selected_order_str = st.selectbox("Órdenes Pendientes", list(pending_orders.keys()))
            order = pending_orders[selected_order_str]

            if st.button("Buscar Ruta y Completar Entrega"):
                pathfinder = Pathfinder(self.graph)
                path, cost = pathfinder.find_path(order.origin, order.destination)
                
                if path:
                    order.deliver(cost)
                    self.clients.get(order.client_id).increment_orders()
                    self.avl.add_route(path)
                    st.session_state.path_to_highlight = path
                    st.success(f"¡Entrega completada! Costo: {cost:.2f}")
                    time.sleep(1); st.rerun()
                else:
                    st.error("No se encontró una ruta viable.")

    def _clients_orders_tab(self):
        st.header("👤 Clientes y Órdenes 📦")
        st.json({"Clientes": [c.to_dict() for c in self.clients.values()], "Órdenes": [o.to_dict() for o in self.orders.values()]})
        
    def _route_analytics_tab(self):
        st.header("📊 Analítica de Rutas (AVL)")
        if not self.avl.root:
            st.info("Aún no hay rutas para analizar."); return
        
        st.subheader("Rutas más Frecuentes")
        st.table(self.avl.get_frequent_routes())
        
        st.subheader("Visualización del Árbol AVL")
        visualizer = AVLVisualizer()
        visualizer.build_graph(self.avl.root)
        fig = visualizer.draw()
        if fig: st.pyplot(fig)

    def _general_statistics_tab(self):
        st.header("📈 Estadísticas Generales")
        if not self.graph:
            st.warning("Primero debe iniciar una simulación."); return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Gráfico de Torta
        role_counts = Counter(v.role for v in self.graph.vertices.values())
        ax1.pie(role_counts.values(), labels=role_counts.keys(), autopct='%1.1f%%', startangle=90)
        ax1.set_title("Proporción de Nodos por Rol")
        
        # Gráfico de Barras
        delivered_dest = [o.destination for o in self.orders.values() if o.status == 'Delivered']
        if delivered_dest:
            dest_counts = Counter(delivered_dest)
            ax2.bar(dest_counts.keys(), dest_counts.values())
            ax2.set_title("Nodos de Destino Más Visitados")
        else:
            ax2.text(0.5, 0.5, "Sin entregas completadas", ha='center')

        st.pyplot(fig)