# Archivo: sim/simulation.py
import streamlit as st
import matplotlib.pyplot as plt
from collections import Counter
import random
import time

# --- Importaciones para algoritmos y visualización ---
from visual.map.map_builder import MapBuilder
from streamlit_folium import st_folium
from sim.mst_finder import MSTFinder
from sim.pathfinder import Pathfinder # Dijkstra
from sim.floyd_warshall_finder import FloydWarshallFinder # Floyd-Warshall

from sim.simulation_initializer import SimulationInitializer
from domain.client import Client
from domain.order import Order
from tda.hashmap import HashMap
from tda.avl import AVLTree
from visual.avl_visualizer import AVLVisualizer

class Simulation:
    def __init__(self):
        # Inicialización de variables de estado
        self.graph = None
        self.fw_finder = None
        self.initializer = SimulationInitializer()
        self.clients = HashMap()
        self.orders = HashMap()
        self.avl = AVLTree()
        self.order_counter = 1
        # Limpiar estados de sesión al iniciar
        for key in ['path_to_highlight', 'show_mst', 'mst_edges']:
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

        st.info(f"Se crearán aproximadamente:\n- {int(n_nodes*0.2)} almacenamiento\n- {int(n_nodes*0.2)} recarga\n- {int(n_nodes*0.6)} clientes")

        if st.button("🚀 Iniciar Simulación"):
            self.__init__()
            with st.spinner('Generando grafo y pre-calculando rutas con Floyd-Warshall...'):
                self.graph = self.initializer.generate_graph(n_nodes, m_edges)
                self.fw_finder = FloydWarshallFinder(self.graph)
            
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
            st.success("¡Simulación generada y rutas pre-calculadas!")

    def _explore_network_tab(self):
        st.header("🌍 Visualización y Procesamiento de Rutas")
        if not self.graph:
            st.warning("Primero debe iniciar una simulación."); return

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Mapa de la Red Logística")
            map_builder = MapBuilder(self.graph)
            mst_edges_to_show = st.session_state.get('mst_edges', None)
            folium_map = map_builder.build_map(st.session_state.get('path_to_highlight'), mst_edges=mst_edges_to_show)
            st_folium(folium_map, width=725, height=500, key="mapa")

        with col2:
            st.subheader("Procesar Órdenes")
            algorithm = st.radio(
                "Seleccione el algoritmo de búsqueda:",
                ('Dijkstra (En tiempo real)', 'Floyd-Warshall (Pre-calculado)'),
                key='algo_selector'
            )
            pending_orders = {f"Orden #{o.order_id} ({o.origin} -> {o.destination})": o for o in self.orders.values() if o.status == 'Pending'}

            if pending_orders:
                selected_order_str = st.selectbox("Seleccione una Orden Pendiente:", list(pending_orders.keys()))
                order = pending_orders[selected_order_str]
                if st.button("Buscar Ruta y Completar Entrega"):
                    chosen_algo = "dijkstra" if "Dijkstra" in algorithm else "floyd_warshall"
                    self._process_delivery(order, chosen_algo)
            else:
                st.success("¡Felicidades! No hay órdenes pendientes.")
            
            st.divider()
            st.subheader("Análisis de Red")
            if st.button("Mostrar/Ocultar MST (Kruskal)"):
                self._toggle_mst_display()

    def _toggle_mst_display(self):
        if not st.session_state.get('show_mst', False):
            mst_finder = MSTFinder(self.graph)
            st.session_state.mst_edges = mst_finder.find_mst()
            st.session_state.show_mst = True
        else:
            st.session_state.mst_edges = None
            st.session_state.show_mst = False
        st.rerun()

    def _process_delivery(self, order, algorithm):
        path, cost = None, float('inf')
        
        with st.spinner(f"Calculando ruta con {algorithm.replace('_', ' ').title()}..."):
            if algorithm == "dijkstra":
                pathfinder = Pathfinder(self.graph)
                path, cost = pathfinder.find_path(order.origin, order.destination)
            elif algorithm == "floyd_warshall":
                path, cost = self.fw_finder.get_path(order.origin, order.destination)
        
        if path:
            order.deliver(cost)
            client_obj = self.clients.get(order.client_id)
            if client_obj: client_obj.increment_orders()
            self.avl.add_route(path)
            st.session_state.path_to_highlight = path
            
            st.success(f"¡Entrega completada! Costo total: {cost:.2f}")
            st.info(f"Ruta: {' → '.join([v.id for v in path])}")
            time.sleep(2); st.rerun()
        else:
            st.error("No se encontró una ruta viable.")

    def _clients_orders_tab(self):
        st.header("👤 Clientes y Órdenes 📦")
        if not self.clients.values() and not self.orders.values():
            st.warning("No hay datos para mostrar. Por favor, inicie una simulación.")
            return

        st.subheader("Clientes Registrados")
        st.json([c.to_dict() for c in self.clients.values()])
        st.subheader("Historial de Órdenes")
        st.json([o.to_dict() for o in self.orders.values()])

    def _route_analytics_tab(self):
        st.header("📊 Analítica de Rutas (Árbol AVL)")
        # --- CÓDIGO CORREGIDO Y ORGANIZADO ---
        if not self.avl.root:
            st.info("Aún no se han completado rutas para poder analizar.")
            return
        
        st.subheader("Rutas Más Frecuentes")
        frequent_routes = self.avl.get_frequent_routes()
        st.table(frequent_routes)
        
        st.subheader("Visualización del Árbol AVL de Rutas")
        with st.spinner("Generando visualización del árbol..."):
            visualizer = AVLVisualizer()
            visualizer.build_graph(self.avl.root)
            fig = visualizer.draw()
            if fig:
                # Pasamos la figura directamente a st.pyplot para evitar la advertencia
                st.pyplot(fig)
            else:
                st.warning("No se pudo generar la visualización del árbol.")

    def _general_statistics_tab(self):
        st.header("📈 Estadísticas Generales de la Simulación")
        # --- CÓDIGO CORREGIDO Y ORGANIZADO ---

        # 1. Añadimos un chequeo para evitar el error si la simulación no ha iniciado
        if not self.graph:
            st.warning("Primero debe iniciar una simulación.")
            return
        
        # 2. Creamos la figura y los ejes
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # 3. Gráfico de Torta: Proporción de Nodos por Rol
        role_counts = Counter(v.role for v in self.graph.vertices.values())
        ax1.pie(role_counts.values(), labels=role_counts.keys(), autopct='%1.1f%%', startangle=90, colors=['skyblue', 'lightgreen', 'sandybrown'])
        ax1.set_title("Proporción de Nodos por Rol")
        ax1.axis('equal')
        
        # 4. Gráfico de Barras: Nodos de Destino Más Visitados
        delivered_destinations = [o.destination for o in self.orders.values() if o.status == 'Delivered']
        if delivered_destinations:
            dest_counts = Counter(delivered_destinations)
            nodes = list(dest_counts.keys())
            visits = list(dest_counts.values())
            ax2.bar(nodes, visits, color='cornflowerblue')
            ax2.set_title("Nodos de Destino Más Visitados")
            ax2.set_xlabel("ID del Nodo")
            ax2.set_ylabel("Número de Entregas")
            plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")
        else:
            ax2.text(0.5, 0.5, "Aún no hay entregas completadas.", ha='center', va='center')
            ax2.set_title("Nodos de Destino Más Visitados")
            ax2.set_xticks([])
            ax2.set_yticks([])

        # 5. Mostramos la figura en Streamlit de la forma recomendada
        st.pyplot(fig)