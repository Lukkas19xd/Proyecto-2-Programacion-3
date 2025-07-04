import uuid
from datetime import datetime

class Order:
    """
    Representa un pedido en el sistema.
    """
    def __init__(self, client, origin: str, destination: str, priority: str = "Normal"):
        """
        Constructor de la orden.
        
        Args:
            client (Client): El objeto cliente que realiza la orden.
            origin (str): El ID del nodo de origen (almacenamiento).
            destination (str): El ID del nodo de destino (cliente).
            priority (str): La prioridad del pedido.
        """
        self.order_id = str(uuid.uuid4())
        # Aquí se usa el objeto client para obtener sus datos
        self.client_id = client.id
        self.client_name = client.name
        self.origin = origin
        self.destination = destination
        self.status = "Pending"
        self.creation_date = datetime.now()
        self.delivery_date = None
        self.total_cost = 0
        self.priority = priority

    def complete_order(self, cost: float):
        """Marca la orden como completada."""
        self.status = "Completed"
        self.delivery_date = datetime.now()
        self.total_cost = cost

    def to_dict(self):
        """Convierte el objeto a un diccionario para visualización."""
        return {
            "order_id": self.order_id,
            "client_id": self.client_id,
            "client_name": self.client_name,
            "origin": self.origin,
            "destination": self.destination,
            "status": self.status,
            "creation_date": self.creation_date.isoformat(),
            "delivery_date": self.delivery_date.isoformat() if self.delivery_date else "N/A",
            "priority": self.priority,
            "total_cost": f"{self.total_cost:.2f}"
        }