import networkx as nx
import matplotlib.pyplot as plt

class NetworkXAdapter:
    def __init__(self, graph):
        self.graph = graph
        self.nx_graph = nx.Graph()
        self._build_nx_graph()
        self.pos = nx.spring_layout(self.nx_graph, seed=42)

    def _build_nx_graph(self):
        color_map = {"storage": "blue", "recharge": "green", "client": "orange"}
        for v in self.graph.vertices.values():
            self.nx_graph.add_node(v.id, color=color_map.get(v.role, "grey"))
        for e in self.graph.edges:
            self.nx_graph.add_edge(e.origin.id, e.destination.id, weight=e.weight)

    def draw(self, highlighted_path=None):
        fig, ax = plt.subplots(figsize=(12, 8))
        colors = [data['color'] for node, data in self.nx_graph.nodes(data=True)]
        
        nx.draw(self.nx_graph, self.pos, with_labels=True, node_color=colors, ax=ax, node_size=700)
        edge_labels = nx.get_edge_attributes(self.nx_graph, 'weight')
        nx.draw_networkx_edge_labels(self.nx_graph, self.pos, edge_labels=edge_labels, ax=ax)

        if highlighted_path:
            path_ids = [v.id for v in highlighted_path]
            path_edges = list(zip(path_ids, path_ids[1:]))
            nx.draw_networkx_nodes(self.nx_graph, self.pos, nodelist=path_ids, node_color='red', node_size=700, ax=ax)
            nx.draw_networkx_edges(self.nx_graph, self.pos, edgelist=path_edges, edge_color='red', width=2.5, ax=ax)
            
        return fig