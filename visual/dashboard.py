import streamlit as st
import matplotlib.pyplot as plt
from collections import Counter
import time

# --- Importaciones de Módulos del Proyecto ---
from sim.simulation import Simulation
from visual.map.map_builder import MapBuilder # Importamos la CLASE
from streamlit_folium import st_folium
from visual.avl_visualizer import AVLVisualizer
from visual.report_generator import generate_pdf_report
from sim.mst_finder import MSTFinder
from sim.pathfinder import Pathfinder

def main_dashboard(sim: Simulation):
    """
    Función principal que construye y ejecuta el dashboard de Streamlit.
    Ahora acepta la instancia de la simulación como argumento.
    """
    st.title("📦 Sistema Logístico Autónomo con Drones")
    
    tabs = st.tabs(["🔄 Simulación", "🌍 Explorar Red", "👤 Clientes y Órdenes", "📊 Analítica de Rutas", "📈 Estadísticas Generales"])

    # --- Pestaña 1: Simulación ---
    with tabs[0]:
        st.header("🔧 Configuración de la Simulación")
        n_nodes = st.slider("Número de Nodos", 10, 150, 15, key="nodes_slider_main")
        m_edges = st.slider("Número de Aristas", n_nodes - 1, 300, 20, key="edges_slider_main")
        n_orders = st.slider("Órdenes Iniciales", 1, 100, 10, key="orders_slider_main")

        if st.button("🚀 Iniciar/Reiniciar Simulación"):
            with st.spinner('Generando nueva simulación...'):
                # Usamos el método de setup para re-inicializar la instancia 'sim'
                sim._setup_simulation(n_nodes, m_edges, n_orders)
            st.success("¡Simulación generada!")
            st.rerun()

    # --- Pestaña 2: Explorar Red ---
    with tabs[1]:
        st.header("🌍 Visualización y Procesamiento de Rutas")
        if not sim.graph:
            st.warning("Primero debe iniciar una simulación.")
        else:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Mapa de la Red Logística")
                map_builder = MapBuilder(sim.graph)
                folium_map = map_builder.build_map(st.session_state.get('path_to_highlight'), st.session_state.get('mst_edges'))
                st_folium(folium_map, width=725, height=500, key="mapa_principal")
            
            with col2:
                st.subheader("Procesar Órdenes")
                algorithm = st.radio("Algoritmo:", ('Dijkstra', 'Floyd-Warshall'), key="algo_radio")
                
                pending_orders = {f"Orden #{o.order_id[:8]} ({o.origin} -> {o.destination})": o for o in sim.orders if o.status == 'Pending'}
                if pending_orders:
                    selected_order_str = st.selectbox("Seleccione Orden:", list(pending_orders.keys()))
                    if st.button("Buscar Ruta y Completar"):
                        order = pending_orders[selected_order_str]
                        sim._process_delivery(order, algorithm.lower())
                else:
                    st.success("No hay órdenes pendientes.")
                
                st.divider()
                st.subheader("Análisis de Red")
                if st.button("Mostrar/Ocultar MST"):
                    sim._toggle_mst_display()

    # --- Pestaña 3: Clientes y Órdenes ---
    with tabs[2]:
        st.header("👤 Clientes y Órdenes")
        if sim.clients:
            st.subheader("Clientes Registrados")
            st.json([c.to_dict() for c in sim.clients.values()])
            st.subheader("Historial de Órdenes")
            st.json([o.to_dict() for o in sim.orders])
        else:
            st.info("No hay datos que mostrar. Inicie una simulación.")

    # --- Pestaña 4: Analítica de Rutas ---
    with tabs[3]:
        st.header("📊 Analítica de Rutas (AVL)")
        if sim.route_frequency_avl.root:
            st.subheader("Rutas Frecuentes")
            st.table(sim.get_frequent_routes())
            
            st.subheader("Visualización del Árbol AVL")
            visualizer = AVLVisualizer(sim.route_frequency_avl)
            fig = visualizer.plot_tree()
            if fig: st.pyplot(fig)
            
            st.divider()
            st.subheader("Generar Informe")
            if st.button("Generar Informe PDF"):
                pdf_path = generate_pdf_report(sim)
                if pdf_path:
                    with open(pdf_path, "rb") as f:
                        st.download_button("📥 Descargar Informe PDF", f, file_name="informe_simulacion.pdf")
        else:
            st.info("No hay rutas completadas para analizar.")
            
    # --- Pestaña 5: Estadísticas Generales ---
    with tabs[4]:
        st.header("📈 Estadísticas Generales")
        if sim.graph:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # Gráfico de Torta
            role_counts = sim.get_node_roles_distribution()
            ax1.pie(role_counts.values(), labels=[k.title() for k in role_counts.keys()], autopct='%1.1f%%', startangle=90)
            ax1.set_title("Proporción de Nodos por Rol")
            
            # Gráfico de Barras
            visited_clients = sim.get_most_visited_nodes("client")
            if visited_clients:
                nodes = [item['node_id'] for item in visited_clients]
                visits = [item['visits'] for item in visited_clients]
                ax2.bar(nodes, visits)
                ax2.set_title("Clientes Más Visitados")
                plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")
            else:
                ax2.text(0.5, 0.5, "Sin entregas.", ha='center')
                ax2.set_title("Clientes Más Visitados")
            
            st.pyplot(fig)
        else:
            st.info("No hay datos para las estadísticas.")