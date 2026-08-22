from Vehicle import Vehicle
class Truck(Vehicle):

    def __init__(self, license_plate):
        super().__init__(license_plate)

    def calculate_cost(self):
        hours = self.get_duration_hours()

        hours = max(1, hours)

        return hours * 30

    def get_vehicle_type(self):
        return "Truck"