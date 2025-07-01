import networkx as nx
import matplotlib.pyplot as plt

class AVLVisualizer:
    """Clase para dibujar el árbol AVL de rutas."""
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph(self, root_node):
        self.graph.clear()
        if root_node: self._add_node_and_edges(root_node)

    def _add_node_and_edges(self, node):
        if not node: return
        label = f"{node.key}\nFreq: {node.freq}"
        self.graph.add_node(node.key, label=label)
        if node.left:
            self.graph.add_edge(node.key, node.left.key)
            self._add_node_and_edges(node.left)
        if node.right:
            self.graph.add_edge(node.key, node.right.key)
            self._add_node_and_edges(node.right)

    def draw(self):
        if not self.graph.nodes: return None
        plt.figure(figsize=(14, 9))
        try:
            # Intenta usar un layout jerárquico si graphviz está instalado
            pos = nx.nx_agraph.graphviz_layout(self.graph, prog='dot')
        except ImportError:
            # Alternativa si no está instalado
            pos = nx.spring_layout(self.graph, seed=42)
        
        labels = nx.get_node_attributes(self.graph, 'label')
        nx.draw(self.graph, pos, labels=labels, with_labels=True, node_color='skyblue', node_size=5000, font_size=9, arrows=True)
        plt.title("Visualización del Árbol AVL de Rutas")
        return plt