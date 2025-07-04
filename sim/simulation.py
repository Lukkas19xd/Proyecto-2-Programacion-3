# Archivo: sim/simulation.py
import streamlit as st
import matplotlib.pyplot as plt
from collections import Counter
import random
import time

# --- Nuevas importaciones para el mapa y MST ---
from visual.map.map_builder import MapBuilder
from streamlit_folium import st_folium
from sim.mst_finder import MSTFinder # <-- Importamos el buscador de MST

from sim.simulation_initializer import SimulationInitializer
from sim.pathfinder import Pathfinder
from domain.client import Client
from domain.order import Order
from tda.hashmap import HashMap
from tda.avl import AVLTree
from visual.avl_visualizer import AVLVisualizer

class Simulation:
    def __init__(self):
        # Inicialización de variables de estado
        self.graph = None
        self.initializer = SimulationInitializer()
        self.clients = HashMap()
        self.orders = HashMap()
        self.avl = AVLTree()
        self.order_counter = 1
        # Limpiar estados de sesión al iniciar
        for key in ['path_to_highlight', 'show_mst']:
            if key in st.session_state:
                del st.session_state[key]

    def run_dashboard(self):
        st.title("📦 Sistema Logístico Autónomo con Drones")
        tabs = st.tabs(["🔄 Simulación", "🌍 Explorar Red", "👤 Clientes y Órdenes", "📊 Analítica de Rutas", "📈 Estadísticas Generales"])

        with tabs[0]: self._run_simulation_tab()
        with tabs[1]: self._explore_network_tab()
        with tabs[2]: self._clients_orders_tab()
        with tabs[3]: self._route_analytics_tab()
        with tabs[4]: self._general_statistics_tab()

    def _run_simulation_tab(self):
        st.header("🔧 Configuración de la Simulación")
        n_nodes = st.slider("Número de Nodos", 10, 150, 15, key="n_nodes")
        m_edges = st.slider("Número de Aristas", n_nodes - 1, 300, 20, key="m_edges")
        n_orders = st.slider("Número de Órdenes", 1, 500, 10, key="n_orders")

        st.info(f"Se crearán aproximadamente:\n- {int(n_nodes*0.2)} nodos de almacenamiento (20%)\n- {int(n_nodes*0.2)} nodos de recarga (20%)\n- {int(n_nodes*0.6)} nodos de cliente (60%)")

        if st.button("🚀 Iniciar Simulación"):
            self.__init__()
            with st.spinner('Generando grafo con coordenadas geoespaciales...'):
                self.graph = self.initializer.generate_graph(n_nodes, m_edges)

            client_nodes = self.graph.get_vertices_by_role("client")
            storage_nodes = self.graph.get_vertices_by_role("storage")

            for node in client_nodes:
                self.clients.insert(node.id, Client(node.id, f"Cliente_{node.id}"))

            if client_nodes and storage_nodes:
                for _ in range(n_orders):
                    client_node = random.choice(client_nodes)
                    storage_node = random.choice(storage_nodes)
                    self.orders.insert(self.order_counter, Order(self.order_counter, client_node.id, storage_node.id, client_node.id))
                    self.order_counter += 1
            st.success("¡Simulación generada con éxito!")

    def _explore_network_tab(self):
        st.header("🌍 Visualización y Procesamiento de Rutas")
        if not self.graph:
            st.warning("Primero debe iniciar una simulación."); return

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Mapa de la Red Logística")
            map_builder = MapBuilder(self.graph)
            
            # Pasar las aristas del MST al constructor del mapa si existen en el estado
            mst_edges_to_show = st.session_state.get('mst_edges', None)
            folium_map = map_builder.build_map(st.session_state.get('path_to_highlight'), mst_edges=mst_edges_to_show)

            st_folium(folium_map, width=725, height=500, key="mapa")

        with col2:
            st.subheader("Procesar Órdenes")
            pending_orders = {f"Orden #{o.order_id} ({o.origin} -> {o.destination})": o for o in self.orders.values() if o.status == 'Pending'}

            if pending_orders:
                selected_order_str = st.selectbox("Seleccione una Orden Pendiente:", list(pending_orders.keys()))
                order = pending_orders[selected_order_str]
                if st.button("Buscar Ruta y Completar Entrega"):
                    self._process_delivery(order)
            else:
                st.success("¡Felicidades! No hay órdenes pendientes.")
            
            st.divider()
            
            # --- SECCIÓN PARA MOSTRAR EL MST ---
            st.subheader("Análisis de Red")
            if st.button("Mostrar/Ocultar MST (Kruskal)"):
                if not st.session_state.get('show_mst', False):
                    # Si no se está mostrando, calcularlo y guardarlo
                    mst_finder = MSTFinder(self.graph)
                    st.session_state.mst_edges = mst_finder.find_mst()
                    st.session_state.show_mst = True
                else:
                    # Si ya se está mostrando, ocultarlo
                    st.session_state.mst_edges = None
                    st.session_state.show_mst = False
                st.rerun() # Refrescar para actualizar el mapa

    def _process_delivery(self, order):
        with st.spinner("Calculando la ruta óptima con Dijkstra..."):
            pathfinder = Pathfinder(self.graph)
            path, cost = pathfinder.find_path(order.origin, order.destination)
        
        if path:
            order.deliver(cost)
            client_obj = self.clients.get(order.client_id)
            if client_obj: client_obj.increment_orders()
            self.avl.add_route(path)
            st.session_state.path_to_highlight = path
            
            st.success(f"¡Entrega completada! Costo total: {cost:.2f}")
            st.info(f"Ruta: {' → '.join([v.id for v in path])}")
            time.sleep(2)
            st.rerun()
        else:
            st.error("No se encontró una ruta viable con la autonomía actual.")

    def _clients_orders_tab(self):
        st.header("👤 Clientes y Órdenes 📦")
        if not self.clients.values() and not self.orders.values():
            st.warning("No hay datos para mostrar. Por favor, inicie una simulación."); return
        
        st.subheader("Clientes Registrados")
        st.json([c.to_dict() for c in self.clients.values()])
        st.subheader("Historial de Órdenes")
        st.json([o.to_dict() for o in self.orders.values()])

    def _route_analytics_tab(self):
        st.header("📊 Analítica de Rutas (Árbol AVL)")
        if not self.avl.root:
            st.info("Aún no se han completado rutas para poder analizar."); return
        
        st.subheader("Rutas Más Frecuentes")
        st.table(self.avl.get_frequent_routes())
        st.subheader("Visualización del Árbol AVL de Rutas")
        with st.spinner("Generando visualización del árbol..."):
            visualizer = AVLVisualizer()
            visualizer.build_graph(self.avl.root)
            fig = visualizer.draw()
            if fig: st.pyplot(fig)

    def _general_statistics_tab(self):
        st.header("📈 Estadísticas Generales de la Simulación")
        if not self.graph:
            st.warning("Primero debe iniciar una simulación."); return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        role_counts = Counter(v.role for v in self.graph.vertices.values())
        ax1.pie(role_counts.values(), labels=role_counts.keys(), autopct='%1.1f%%', startangle=90, colors=['skyblue', 'lightgreen', 'sandybrown'])
        ax1.set_title("Proporción de Nodos por Rol")
        ax1.axis('equal')
        
        delivered_dest = [o.destination for o in self.orders.values() if o.status == 'Delivered']
        if delivered_dest:
            dest_counts = Counter(delivered_dest)
            ax2.bar(dest_counts.keys(), dest_counts.values(), color='cornflowerblue')
            ax2.set_title("Nodos de Destino Más Visitados")
            ax2.set_xlabel("ID del Nodo")
            ax2.set_ylabel("Número de Entregas")
            plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")
        else:
            ax2.text(0.5, 0.5, "Aún no hay entregas completadas.", ha='center', va='center')
            ax2.set_title("Nodos de Destino Más Visitados")
        
        st.pyplot(fig)