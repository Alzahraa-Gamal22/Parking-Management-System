from Vehicle import Vehicle
class ParkingLot:

    def __init__(self, name):
        self.__name = name
        self.__spots = []

    # Add parking spot
    def add_spot(self, spot):
        self.__spots.append(spot)

    # Get all spots
    def get_spots(self):
        return self.__spots

    # Find vehicle by license plate
    def find_vehicle(self, license_plate):

        for spot in self.__spots:

            if spot.is_occupied():

                vehicle = spot.get_vehicle()

                if vehicle.get_license_plate() == license_plate:
                    return vehicle, spot

        return None, None

    # Find available spot
    def find_available_spot(self, vehicle):

        for spot in self.__spots:

            if spot.can_fit_vehicle(vehicle):
                return spot

        return None

    # Vehicle Entry
    def vehicle_entry(self, vehicle, entry_time=None):
        # Check if vehicle is already inside
        existing_vehicle, existing_spot = self.find_vehicle(
            vehicle.get_license_plate()
        )

        if existing_vehicle is not None:
            print("Vehicle is already inside the parking lot.")
            return False

        # Find available spot
        spot = self.find_available_spot(vehicle)

        if spot is None:
            print("No available parking spot.")
            return False

        # Enter vehicle
        vehicle.enter(entry_time)

        # Park vehicle
        if spot.park_vehicle(vehicle):

            print("\nVehicle entered successfully.")
            print(f"Vehicle: {vehicle.get_vehicle_type()}")
            print(f"License Plate: {vehicle.get_license_plate()}")
            print(f"Spot: {spot.get_spot_id()}")
            print(f"Entry Time: {vehicle.get_entry_time()}")

            return True

        return False

    # Vehicle Exit
    def vehicle_exit(self, license_plate, exit_time=None):

        vehicle, spot = self.find_vehicle(license_plate)

        if vehicle is None:
            print("Vehicle not found in the parking lot.")
            return False

        # Set exit time
        vehicle.exit(exit_time)

        # Calculate cost
        cost = vehicle.calculate_cost()

        # Remove vehicle
        spot.remove_vehicle()

        print("\nVehicle exited successfully.")
        print(f"Vehicle: {vehicle.get_vehicle_type()}")
        print(f"License Plate: {vehicle.get_license_plate()}")
        print(f"Spot: {spot.get_spot_id()}")
        print(f"Entry Time: {vehicle.get_entry_time()}")
        print(f"Exit Time: {vehicle.get_exit_time()}")
        print(f"Duration: {vehicle.get_duration_hours():.2f} hours")
        print(f"Total Cost: {cost:.2f} EGP")

        return True

    # Display parking spots
    def display_parking_status(self):

        print("\n========== Parking Status ==========")

        for spot in self.__spots:
            print(spot)

        print("====================================")