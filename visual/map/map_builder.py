# visual/map/map_builder.py
import folium

class MapBuilder:
    def __init__(self, graph):
        self.graph = graph

    def build_map(self, highlighted_path=None):
        # Coordenadas de Temuco para centrar el mapa
        map_center = [-38.7359, -72.5904]
        m = folium.Map(location=map_center, zoom_start=13)

        # Colores para cada rol
        color_map = {"storage": "blue", "recharge": "green", "client": "orange"}

        # Dibujar aristas (líneas grises)
        for edge in self.graph.edges:
            start_node = edge.origin
            end_node = edge.destination
            folium.PolyLine(
                locations=[(start_node.lat, start_node.lon), (end_node.lat, end_node.lon)],
                color="grey",
                weight=2,
                opacity=0.5
            ).add_to(m)

        # Dibujar nodos (círculos de colores)
        for node in self.graph.vertices.values():
            folium.CircleMarker(
                location=[node.lat, node.lon],
                radius=5,
                color=color_map.get(node.role, "black"),
                fill=True,
                fill_color=color_map.get(node.role, "black"),
                tooltip=f"ID: {node.id}\nRol: {node.role}"
            ).add_to(m)

        # Si hay una ruta para resaltar, dibujarla en rojo
        if highlighted_path:
            path_coords = [(node.lat, node.lon) for node in highlighted_path]
            folium.PolyLine(
                locations=path_coords,
                color="red",
                weight=4,
                opacity=0.8,
                tooltip="Ruta Seleccionada"
            ).add_to(m)
        
        return m