import folium

class MapBuilder:
    def __init__(self, graph):
        self.graph = graph
        self.map_center = [-38.7359, -72.5904]

    def build_map(self, highlight_route=None, mst_edges=None):
        m = folium.Map(location=self.map_center, zoom_start=13)
        if not self.graph: return m
        self._draw_nodes(m)
        self._draw_edges(m)
        if highlight_route: self._highlight_route(m, highlight_route)
        if mst_edges: self._draw_mst(m, mst_edges)
        return m

    def _draw_nodes(self, m):
        color_map = {"Cliente": "blue", "Almacenamiento": "green", "Recarga": "orange"}
        for node_id, vertex in self.graph.vertices.items():
            folium.Marker(
                location=[vertex.lat, vertex.lon],
                popup=f"ID: {node_id}<br>Rol: {vertex.role}",
                icon=folium.Icon(color=color_map.get(vertex.role, "gray"))
            ).add_to(m)

    def _draw_edges(self, m):
        """Dibuja las aristas usando los atributos correctos 'u' y 'v'."""
        for edge in self.graph.edges:
            # **AQUÍ ESTÁ LA CORRECCIÓN FINAL Y DEFINITIVA**
            start_node = self.graph.get_vertex(edge.u)
            end_node = self.graph.get_vertex(edge.v)
            if start_node and end_node:
                points = [(start_node.lat, start_node.lon), (end_node.lat, end_node.lon)]
                folium.PolyLine(points, color='gray', weight=1.5, opacity=0.5).add_to(m)

    def _highlight_route(self, m, route_ids):
        route_points = [(self.graph.get_vertex(nid).lat, self.graph.get_vertex(nid).lon) for nid in route_ids if self.graph.get_vertex(nid)]
        if len(route_points) > 1:
            folium.PolyLine(route_points, color='red', weight=4, opacity=1).add_to(m)

    def _draw_mst(self, m, mst_edges):
        for u_id, v_id in mst_edges:
            start_node = self.graph.get_vertex(u_id)
            end_node = self.graph.get_vertex(v_id)
            if start_node and end_node:
                points = [(start_node.lat, start_node.lon), (end_node.lat, end_node.lon)]
                folium.PolyLine(points, color='purple', weight=3, opacity=0.7, dash_array='5, 5').add_to(m)