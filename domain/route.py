class Route:
    def __init__(self, path, cost):
        self.path = path
        self.cost = cost

    def __str__(self):
        return " → ".join([v.id for v in self.path])

    def to_key(self):
        return str(self)
