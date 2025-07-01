class AVLNode:
    """Nodo para el árbol AVL, almacena la ruta y su frecuencia."""
    def __init__(self, key, freq=1):
        self.key = key
        self.freq = freq
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    """Árbol AVL para registrar y contar la frecuencia de las rutas utilizadas."""
    def __init__(self):
        self.root = None

    def add_route(self, path):
        key = " → ".join([v.id for v in path])
        self.root = self._insert(self.root, key)

    def _insert(self, root, key):
        if not root: return AVLNode(key)
        if key == root.key:
            root.freq += 1
            return root
        elif key < root.key:
            root.left = self._insert(root.left, key)
        else:
            root.right = self._insert(root.right, key)
        
        root.height = 1 + max(self._height(root.left), self._height(root.right))
        balance = self._get_balance(root)

        if balance > 1 and key < root.left.key: return self._rotate_right(root)
        if balance < -1 and key > root.right.key: return self._rotate_left(root)
        if balance > 1 and key > root.left.key:
            root.left = self._rotate_left(root.left)
            return self._rotate_right(root)
        if balance < -1 and key < root.right.key:
            root.right = self._rotate_right(root.right)
            return self._rotate_left(root)
        return root

    def get_frequent_routes(self):
        routes = self._inorder(self.root)
        return sorted(routes, key=lambda item: item[1], reverse=True)

    def _inorder(self, root, result=None):
        if result is None: result = []
        if root:
            self._inorder(root.left, result)
            result.append((root.key, root.freq))
            self._inorder(root.right, result)
        return result

    def _height(self, node): return node.height if node else 0
    def _get_balance(self, node): return self._height(node.left) - self._height(node.right) if node else 0

    def _rotate_left(self, z):
        y, T2 = z.right, z.right.left
        y.left, z.right = z, T2
        z.height = 1 + max(self._height(z.left), self._height(z.right))
        y.height = 1 + max(self._height(y.left), self._height(y.right))
        return y

    def _rotate_right(self, y):
        x, T2 = y.left, y.left.right
        x.right, y.left = y, T2
        y.height = 1 + max(self._height(y.left), self._height(y.right))
        x.height = 1 + max(self._height(x.left), self._height(x.right))
        return x