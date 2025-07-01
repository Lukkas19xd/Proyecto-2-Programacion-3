import datetime

class Order:
    """Modela un pedido o una orden de entrega."""
    def __init__(self, order_id, client_id, origin, destination):
        self.order_id = order_id
        self.client_id = client_id
        self.origin = origin
        self.destination = destination
        self.status = "Pending"  # Estados: Pending, Delivered
        self.creation_date = datetime.datetime.now()
        self.delivery_date = None
        self.cost = 0.0

    def deliver(self, cost):
        """Marca la orden como entregada y registra el costo y la fecha."""
        self.status = "Delivered"
        self.delivery_date = datetime.datetime.now()
        self.cost = cost

    def to_dict(self):
        """Convierte los datos de la orden a un diccionario para visualización."""
        return {
            "ID Orden": self.order_id,
            "ID Cliente": self.client_id,
            "Origen": self.origin,
            "Destino": self.destination,
            "Status": self.status,
            "Fecha Creación": self.creation_date.strftime("%Y-%m-%d %H:%M"),
            "Fecha Entrega": self.delivery_date.strftime("%Y-%m-%d %H:%M") if self.delivery_date else "N/A",
            "Costo Total": f"{self.cost:.2f}"
        }