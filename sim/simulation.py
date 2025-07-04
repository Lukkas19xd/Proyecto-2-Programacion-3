import streamlit as st
import matplotlib.pyplot as plt
from collections import Counter
import random
import time

# --- Importaciones de Módulos del Proyecto ---
from model.graph import Graph
from domain.client import Client
from domain.order import Order
from tda.avl import AVLTree
from sim.simulation_initializer import SimulationInitializer
from visual.map.map_builder import MapBuilder
from streamlit_folium import st_folium
from sim.mst_finder import MSTFinder
from sim.pathfinder import Pathfinder
from sim.floyd_warshall_finder import FloydWarshallFinder
from visual.report_generator import generate_pdf_report
from visual.avl_visualizer import AVLVisualizer

class Simulation:
    def __init__(self, n_nodes=None, m_edges=None, n_orders=None):
        self.initializer = SimulationInitializer()
        self.graph = None
        self.clients = {}
        self.orders = []
        self.route_frequency_avl = AVLTree()
        self.node_visits = Counter()
        self.fw_finder = None
        
        if n_nodes and m_edges and n_orders:
            self._setup_simulation(n_nodes, m_edges, n_orders)

    def _setup_simulation(self, n_nodes, m_edges, n_orders):
        self.graph = self.initializer.generate_graph(n_nodes, m_edges)
        self.clients = {node.id: Client(node.id, f"Cliente_{node.id}") for node in self.graph.get_vertices_by_role("client")}
        self.orders = self._create_initial_orders(n_orders)
        self.route_frequency_avl = AVLTree()
        self.node_visits = Counter()
        if self.graph:
            self.fw_finder = FloydWarshallFinder(self.graph)

    def run_dashboard(self):
        st.set_page_config(page_title="Sistema Logístico con Drones", layout="wide")
        st.title("📦 Sistema Logístico Autónomo con Drones")
        
        tabs = st.tabs(["🔄 Simulación", "🌍 Explorar Red", "👤 Clientes y Órdenes", "📊 Analítica de Rutas", "📈 Estadísticas Generales"])
        
        with tabs[0]: self._run_simulation_tab()
        with tabs[1]: self._explore_network_tab()
        with tabs[2]: self._clients_orders_tab()
        with tabs[3]: self._route_analytics_tab()
        with tabs[4]: self._general_statistics_tab()

    def _run_simulation_tab(self):
        st.header("🔧 Configuración de la Simulación")
        n_nodes = st.slider("Número de Nodos", 10, 150, 15)
        m_edges = st.slider("Número de Aristas", n_nodes - 1, 300, 20)
        n_orders = st.slider("Órdenes Iniciales", 1, 100, 10)
        
        if st.button("🚀 Iniciar Simulación"):
            with st.spinner('Generando simulación...'):
                self._setup_simulation(n_nodes, m_edges, n_orders)
            st.success("¡Simulación generada!")
            st.rerun()

    def _explore_network_tab(self):
        st.header("🌍 Visualización y Procesamiento de Rutas")
        if not self.graph:
            st.warning("Primero debe iniciar una simulación."); return

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Mapa de la Red Logística")
            map_builder = MapBuilder(self.graph)
            folium_map = map_builder.build_map(st.session_state.get('path_to_highlight'), st.session_state.get('mst_edges'))
            st_folium(folium_map, width=725, height=500, key="mapa")
        with col2:
            st.subheader("Procesar Órdenes")
            algorithm = st.radio("Algoritmo:", ('Dijkstra', 'Floyd-Warshall'))
            pending_orders = {f"Orden #{o.order_id[:8]} ({o.origin} -> {o.destination})": o for o in self.orders if o.status == 'Pending'}
            if pending_orders:
                selected_order_str = st.selectbox("Seleccione Orden:", list(pending_orders.keys()))
                if st.button("Buscar Ruta y Completar"):
                    self._process_delivery(pending_orders[selected_order_str], algorithm.lower())
            else:
                st.success("No hay órdenes pendientes.")
            st.divider()
            st.subheader("Análisis de Red")
            if st.button("Mostrar/Ocultar MST"):
                self._toggle_mst_display()

    def _clients_orders_tab(self):
        st.header("👤 Clientes y Órdenes 📦")
        if not self.clients:
            st.warning("No hay datos. Inicie una simulación."); return
        st.subheader("Clientes Registrados")
        st.json([c.to_dict() for c in self.clients.values()])
        st.subheader("Historial de Órdenes")
        st.json([o.to_dict() for o in self.orders])

    def _route_analytics_tab(self):
        st.header("📊 Analítica de Rutas (AVL)")
        if not self.route_frequency_avl.root:
            st.info("No hay rutas completadas para analizar."); return
        st.subheader("Rutas Más Frecuentes")
        st.table(self.route_frequency_avl.get_frequent_routes())
        st.subheader("Visualización del Árbol AVL")
        visualizer = AVLVisualizer(self.route_frequency_avl)
        fig = visualizer.plot_tree()
        if fig: st.pyplot(fig)
        st.divider()
        st.subheader("Descargar Informe PDF")
        if st.button("Generar Informe"):
            pdf_path = generate_pdf_report(self)
            if pdf_path:
                with open(pdf_path, "rb") as f:
                    st.download_button("📥 Descargar PDF", f, file_name="informe.pdf")

    def _general_statistics_tab(self):
        st.header("📈 Estadísticas Generales")
        if not self.graph:
            st.warning("Inicie una simulación."); return
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # **AQUÍ SE USA EL MÉTODO CORREGIDO**
        role_counts = self.get_node_roles_distribution()
        ax1.pie(role_counts.values(), labels=[k.title() for k in role_counts.keys()], autopct='%1.1f%%', startangle=90)
        ax1.set_title("Proporción de Nodos por Rol")
        
        visited_nodes = self.get_most_visited_nodes("client")
        if visited_nodes:
            nodes = [item['node_id'] for item in visited_nodes]
            visits = [item['visits'] for item in visited_nodes]
            ax2.bar(nodes, visits)
            ax2.set_title("Clientes Más Visitados")
            plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")
        else:
            ax2.text(0.5, 0.5, "Sin entregas.", ha='center')
            ax2.set_title("Clientes Más Visitados")
        st.pyplot(fig)

    def _process_delivery(self, order, algorithm):
        path, cost = None, float('inf')
        if algorithm == "dijkstra":
            pathfinder = Pathfinder(self.graph)
            path, cost = pathfinder.find_path(order.origin, order.destination)
        elif self.fw_finder:
            path, cost = self.fw_finder.get_path(order.origin, order.destination)
        
        if path:
            path_ids = [v.id for v in path]
            order.complete_order(cost)
            self.clients.get(order.client_id).increment_orders()
            self._log_route(path_ids)
            st.session_state['path_to_highlight'] = path_ids
            st.success(f"Entrega completada! Costo: {cost:.2f}")
            time.sleep(1); st.rerun()
        else:
            st.error("No se encontró ruta.")

    def _toggle_mst_display(self):
        if not st.session_state.get('show_mst'):
            st.session_state.mst_edges = MSTFinder(self.graph).find_mst()
            st.session_state.show_mst = True
        else:
            st.session_state.mst_edges = None
            st.session_state.show_mst = False
        st.rerun()
        
    def _log_route(self, route_ids):
        route_key = "->".join(route_ids)
        self.route_frequency_avl.insert(route_key)
        for node_id in route_ids:
            self.node_visits[node_id] += 1
            
    def _create_initial_orders(self, n_orders: int):
        orders = []
        storage_nodes = self.graph.get_vertices_by_role("storage")
        client_nodes = self.graph.get_vertices_by_role("client")
        if not storage_nodes or not client_nodes: return []
        
        for _ in range(n_orders):
            origin = random.choice(storage_nodes)
            destination = random.choice(client_nodes)
            client = self.clients.get(destination.id)
            if client:
                orders.append(Order(client, origin.id, destination.id))
        return orders
        
    def get_most_visited_nodes(self, role):
        ranking = []
        for node_id, visits in self.node_visits.items():
            vertex = self.graph.get_vertex(node_id)
            if vertex and vertex.role.lower() == role.lower():
                ranking.append({"node_id": node_id, "visits": visits})
        return sorted(ranking, key=lambda x: x['visits'], reverse=True)

    # --- MÉTODO AÑADIDO ---
    def get_node_roles_distribution(self):
        """
        Calcula y devuelve un conteo de nodos por cada rol.
        """
        if not self.graph:
            return Counter()
        return Counter(v.role for v in self.graph.vertices.values())