class Client:
    """Modela un cliente en el sistema."""
    def __init__(self, client_id, name):
        self.id = client_id
        self.name = name
        self.total_orders = 0

    def increment_orders(self):
        """Incrementa el contador de pedidos del cliente."""
        self.total_orders += 1

    def to_dict(self):
        """Convierte los datos del cliente a un diccionario para visualización."""
        return {
            "ID Cliente": self.id,
            "Nombre": self.name,
            "Total Pedidos": self.total_orders
        }