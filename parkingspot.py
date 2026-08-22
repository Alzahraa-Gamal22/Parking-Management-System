from Vehicle import Vehicle
class ParkingSpot:

    def __init__(self, spot_id, spot_type):
        self.__spot_id = spot_id
        self.__spot_type = spot_type
        self.__is_occupied = False
        self.__vehicle = None

    # Getters
    def get_spot_id(self):
        return self.__spot_id

    def get_spot_type(self):
        return self.__spot_type

    def is_occupied(self):
        return self.__is_occupied

    def get_vehicle(self):
        return self.__vehicle

    # Check if vehicle can use this spot
    def can_fit_vehicle(self, vehicle):

        if self.__is_occupied:
            return False

        vehicle_type = vehicle.get_vehicle_type()

        if self.__spot_type == "Regular":
            return vehicle_type in ["Car", "Motorcycle"]

        if self.__spot_type == "Large":
            return vehicle_type in ["Car", "Motorcycle", "Truck"]

        return False

    # Park vehicle
    def park_vehicle(self, vehicle):

        if self.can_fit_vehicle(vehicle):
            self.__vehicle = vehicle
            self.__is_occupied = True
            return True

        return False

    # Remove vehicle
    def remove_vehicle(self):

        if not self.__is_occupied:
            return None

        vehicle = self.__vehicle

        self.__vehicle = None
        self.__is_occupied = False

        return vehicle

    def __str__(self):

        if self.__is_occupied:
            vehicle_info = str(self.__vehicle)
            return f"Spot {self.__spot_id} | {self.__spot_type} | Occupied | {vehicle_info}"

        return f"Spot {self.__spot_id} | {self.__spot_type} | Available"
