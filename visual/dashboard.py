# visual/dashboard.py

import streamlit as st
from streamlit_folium import st_folium
import folium  # Asegúrate de tener folium instalado

# Importar las clases y funciones de tu proyecto
from sim.simulation import Simulation
from sim.init_simulation import SimulationInitializer
from visual.map import map_builder
from domain.order import Order

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Sistema Logístico con Drones",
    page_icon="✈️",
    layout="wide"
)

# --- Inicialización del Estado de la Simulación ---
if 'simulation_started' not in st.session_state:
    st.session_state.simulation_started = False
    st.session_state.simulation = None
    st.session_state.map = None
    st.session_state.last_path = None
    st.session_state.last_cost = None
    st.session_state.orders = []

# --- Título Principal ---
st.title("🚁 Sistema Logístico Autónomo con Drones - Fase 2")

# --- Definición de las Pestañas ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1️⃣ Run Simulation",
    "2️⃣ Explore Network",
    "3️⃣ Clients & Orders",
    "4️⃣ Route Analytics",
    "5️⃣ General Statistics"
])

# --- Pestaña 1: Run Simulation ---
with tab1:
    st.header("Configuración de la Simulación")

    # Sliders para configurar la simulación
    n_nodes = st.slider("Número de Nodos (n_nodes)", 10, 150, 15)
    m_edges = st.slider("Número de Aristas (m_edges)", n_nodes - 1, 300, 20)
    n_orders = st.slider("Número de Órdenes (n_orders)", 10, 300, 10)

    # Validar que el número de aristas sea suficiente para un grafo conexo
    if m_edges < n_nodes - 1:
        st.error(f"El número de aristas debe ser al menos {n_nodes - 1} para asegurar un grafo conexo.")
        sim_ready = False
    else:
        sim_ready = True

    # Campo informativo con la distribución de roles
    st.info(
        f"**Distribución de Nodos:**\n"
        f"- **Almacenamiento (20%):** {int(n_nodes * 0.2)}\n"
        f"- **Recarga (20%):** {int(n_nodes * 0.2)}\n"
        f"- **Cliente (60%):** {n_nodes - int(n_nodes * 0.2) - int(n_nodes * 0.2)}"
    )

    if st.button("🚀 Start Simulation", disabled=not sim_ready):
        with st.spinner("Generando grafo y preparando simulación..."):
            initializer = SimulationInitializer(n_nodes, m_edges)
            connected_graph = initializer.generate_connected_graph()

            st.session_state.simulation = Simulation(connected_graph)
            st.session_state.simulation.assign_node_roles()
            st.session_state.simulation_started = True

            st.session_state.last_path = None
            st.session_state.last_cost = None
            st.session_state.orders = []

            st.session_state.map = map_builder.build_map(st.session_state.simulation.graph)

        st.success("¡Simulación iniciada con éxito! Navega a la pestaña 'Explore Network' para comenzar.")

# --- Pestaña 2: Explore Network ---
with tab2:
    st.header("Exploración de la Red y Cálculo de Rutas")

    if not st.session_state.simulation_started:
        st.warning("Por favor, inicie una simulación en la pestaña 'Run Simulation' primero.")
    else:
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Control de Rutas")

            graph_nodes = st.session_state.simulation.graph.vertices
            storage_nodes = [nid for nid, v in graph_nodes.items() if v.role == 'Almacenamiento']
            client_nodes = [nid for nid, v in graph_nodes.items() if v.role == 'Cliente']

            origin_node = st.selectbox("Nodo Origen (Almacenamiento)", options=storage_nodes)
            destination_node = st.selectbox("Nodo Destino (Cliente)", options=client_nodes)

            algorithm = st.radio("Algoritmo de Ruta", ("Dijkstra", "Floyd-Warshall"))

            if st.button("Calculate Route", key="calculate_route"):
                if origin_node and destination_node:
                    path, cost, route_type = st.session_state.simulation.find_path_with_recharge(origin_node, destination_node)

                    if path:
                        st.session_state.last_path = path
                        st.session_state.last_cost = cost

                        st.session_state.map = map_builder.build_map(
                            st.session_state.simulation.graph,
                            highlighted_path=path
                        )
                    else:
                        st.session_state.last_path = None
                        st.session_state.last_cost = None
                        st.error("No se pudo encontrar una ruta viable que cumpla con la autonomía del dron.")
                else:
                    st.warning("Por favor, seleccione un nodo de origen y uno de destino.")

            if st.button("Complete Delivery and Create Order", disabled=not st.session_state.last_path):
                if st.session_state.last_path:
                    new_order = Order(
                        order_id=f"ORD-{len(st.session_state.orders) + 1}",
                        client_id=st.session_state.last_path[-1],
                        origin=st.session_state.last_path[0],
                        destination=st.session_state.last_path[-1],
                        total_cost=st.session_state.last_cost
                    )
                    st.session_state.orders.append(new_order)
                    st.success(f"Orden {new_order.order_id} creada y registrada con éxito!")

                    st.session_state.last_path = None
                    st.session_state.last_cost = None
                    st.session_state.map = map_builder.build_map(st.session_state.simulation.graph)
                else:
                    st.warning("Primero debe calcular una ruta válida.")

            if st.button("Show MST (Kruskal)", disabled=True):
                st.info("Funcionalidad para mostrar el Árbol de Expansión Mínima (MST) pendiente de implementación.")

            if st.session_state.last_path:
                st.subheader("Resumen de Vuelo")
                route_type_msg = "Con Recarga" if st.session_state.simulation.find_path_with_recharge(origin_node, destination_node)[2] == "Con Recarga" else "Directa"
                st.markdown(f"**Tipo de Ruta:** {route_type_msg}")
                st.markdown(f"**Costo Total (energía):** `{st.session_state.last_cost}`")
                st.markdown(f"**Recorrido:** `{' -> '.join(st.session_state.last_path)}`")

        with col2:
            st.subheader("Mapa de la Red")
            if st.session_state.map:
                st_folium(st.session_state.map, width=800, height=600)
            else:
                st.info("El mapa se mostrará aquí una vez que inicie la simulación.")

# --- Pestaña 3: Clients & Orders ---
with tab3:
    st.header("Gestión de Clientes y Órdenes")

    if not st.session_state.simulation_started:
        st.warning("Inicie una simulación para ver los datos de clientes y órdenes.")
    else:
        st.subheader("Lista de Clientes")
        client_data = {nid: {"role": v.role} for nid, v in st.session_state.simulation.graph.vertices.items() if v.role == 'Cliente'}
        st.json(client_data)

        st.subheader("Historial de Órdenes")
        if st.session_state.orders:
            orders_data = [order.__dict__ for order in st.session_state.orders]
            st.json(orders_data)
        else:
            st.info("Aún no se han generado órdenes. Complete una entrega en 'Explore Network'.")

# --- Pestaña 4: Route Analytics ---
with tab4:
    st.header("Análisis de Rutas (AVL)")

    if not st.session_state.simulation_started:
        st.warning("Inicie una simulación y genere rutas para ver las analíticas.")
    else:
        st.info("Funcionalidad para visualizar el árbol AVL de rutas frecuentes pendiente de implementación.")

        if st.button("Generar Informe PDF", disabled=True):
            st.info("La generación de informes en PDF se implementará aquí.")

# --- Pestaña 5: General Statistics ---
with tab5:
    st.header("Estadísticas Generales del Sistema")

    if not st.session_state.simulation_started:
        st.warning("Inicie una simulación para ver las estadísticas.")
    else:
        st.info("Funcionalidad para mostrar gráficos estadísticos pendiente de implementación.")

        st.subheader("Distribución de Nodos por Rol")
        roles = [v.role for v in st.session_state.simulation.graph.vertices.values()]
        role_counts = {role: roles.count(role) for role in set(roles)}

        import pandas as pd
        import matplotlib.pyplot as plt

        df_roles = pd.DataFrame(list(role_counts.items()), columns=['Rol', 'Cantidad'])
        fig, ax = plt.subplots()
        ax.pie(df_roles['Cantidad'], labels=df_roles['Rol'], autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

        st.subheader("Nodos Más Visitados (Pendiente)")
        st.info("El gráfico de barras para nodos más visitados se mostrará aquí.")
