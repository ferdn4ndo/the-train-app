class RollingStock:

    def __init__(self, **options):
        self.operative = True

    def is_operative(self):
        return self.operative


class Locomotive(RollingStock):
    pass


class Car(RollingStock):
    pass


class MaintenanceOfWay(RollingStock):
    pass
