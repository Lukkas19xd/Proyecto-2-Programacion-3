import folium

# Asegúrate de que la función acepte los nuevos parámetros
def build_map(graph, highlighted_path=None, mst_edges=None):
    """
    Construye un mapa de Folium con nodos, aristas, una ruta resaltada y el MST.
    
    Args:
        graph (Graph): El objeto grafo.
        highlighted_path (list, optional): La ruta a resaltar en rojo.
        mst_edges (list, optional): Las aristas del MST a dibujar en azul discontinuo.
    """
    # Coordenada central (ej. Temuco)
    map_center = [-38.7396, -72.5984]
    m = folium.Map(location=map_center, zoom_start=13)

    # 1. Dibujar todos los nodos
    for vertex_id, vertex in graph.vertices.items():
        color_map = {'Almacenamiento': 'blue', 'Recarga': 'orange', 'Cliente': 'green'}
        folium.Marker(
            location=[vertex.lat, vertex.lon],
            popup=f"ID: {vertex_id}<br>Rol: {vertex.role}",
            icon=folium.Icon(color=color_map.get(vertex.role, 'gray'))
        ).add_to(m)

    # 2. Dibujar todas las aristas del grafo base (en gris)
    for u, neighbors in graph.adj.items():
        for v, weight in neighbors.items():
            start_pos = [graph.vertices[u].lat, graph.vertices[u].lon]
            end_pos = [graph.vertices[v].lat, graph.vertices[v].lon]
            folium.PolyLine(
                locations=[start_pos, end_pos],
                color='gray',
                weight=1,
                opacity=0.5
            ).add_to(m)
    
    # 3. Dibujar las aristas del MST si se proporcionan (en azul discontinuo)
    if mst_edges:
        for u, v, weight in mst_edges:
            start_pos = [graph.vertices[u].lat, graph.vertices[u].lon]
            end_pos = [graph.vertices[v].lat, graph.vertices[v].lon]
            folium.PolyLine(
                locations=[start_pos, end_pos],
                tooltip=f"MST Edge: {weight}",
                color='blue',
                weight=3,
                opacity=0.8,
                dash_array='5, 10' # Estilo de línea discontinua
            ).add_to(m)

    # 4. Resaltar la ruta calculada si se proporciona (en rojo)
    if highlighted_path and len(highlighted_path) > 1:
        path_points = [[graph.vertices[node_id].lat, graph.vertices[node_id].lon] for node_id in highlighted_path]
        folium.PolyLine(
            locations=path_points,
            tooltip="Ruta Calculada",
            color='red',
            weight=5,
            opacity=1.0
        ).add_to(m)
        
    return m