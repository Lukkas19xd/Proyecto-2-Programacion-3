class HashMap:
    """Implementación simple de un Hash Map para almacenar clientes y órdenes."""
    def __init__(self, size=100):
        self.size = size
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        return hash(key) % self.size

    def insert(self, key, value):
        index = self._hash(key)
        for i, (k, _) in enumerate(self.table[index]):
            if k == key:
                self.table[index][i] = (key, value)
                return
        self.table[index].append((key, value))

    def get(self, key):
        index = self._hash(key)
        for k, v in self.table[index]:
            if k == key:
                return v
        return None

    def values(self):
        """Retorna todos los valores en el hashmap."""
        return [v for bucket in self.table for (_, v) in bucket]