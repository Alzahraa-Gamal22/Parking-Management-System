import json
import csv
from datetime import datetime

from Parkinglot import ParkingLot
from parkingspot import ParkingSpot
from Car import Car
from Motorcycle import Motorcycle
from Truck import Truck
from exceptions import (
    DuplicateVehicleError,
    VehicleNotFoundError,
    InvalidSpotError,
    DataFileError
)


class DataManager:

    # Maps a vehicle type name to its class (used when loading from JSON)
    VEHICLE_CLASSES = {
        "Car": Car,
        "Motorcycle": Motorcycle,
        "Truck": Truck
    }

    def __init__(self, parking_lot):
        # Reference to the ParkingLot object (built by teammate)
        self.__parking_lot = parking_lot

        # Dictionary: license_plate -> vehicle object (fast lookup)
        self.__vehicles = {}

        # Set: all license plates currently parked (fast duplicate check)
        self.__active_plates = set()

        # List: log of every entry/exit transaction
        self.__transaction_log = []

    # ==========================================
    # Add / Delete / Edit
    # ==========================================

    # Add a vehicle to the parking lot
    def add_vehicle(self, vehicle):

        plate = vehicle.get_license_plate()

        if plate in self.__active_plates:
            raise DuplicateVehicleError(
                f"Vehicle with plate '{plate}' is already parked."
            )

        success = self.__parking_lot.vehicle_entry(vehicle)

        if not success:
            raise InvalidSpotError("No available spot for this vehicle.")

        self.__vehicles[plate] = vehicle
        self.__active_plates.add(plate)

        self.__transaction_log.append({
            "action": "entry",
            "plate": plate,
            "type": vehicle.get_vehicle_type(),
            "time": str(vehicle.get_entry_time())
        })

        return True

    # Remove a vehicle from the parking lot
    def delete_vehicle(self, plate):

        if plate not in self.__active_plates:
            raise VehicleNotFoundError(
                f"Vehicle with plate '{plate}' was not found."
            )

        vehicle = self.__vehicles[plate]

        success = self.__parking_lot.vehicle_exit(plate)

        if not success:
            raise VehicleNotFoundError(
                f"Could not remove vehicle with plate '{plate}'."
            )

        cost = vehicle.calculate_cost()

        self.__transaction_log.append({
            "action": "exit",
            "plate": plate,
            "type": vehicle.get_vehicle_type(),
            "time": str(vehicle.get_exit_time()),
            "cost": cost
        })

        # Remove from our dict/set
        del self.__vehicles[plate]
        self.__active_plates.discard(plate)

        return cost

    # Change an existing spot's type ("Regular" / "Large")
    def edit_spot_type(self, spot_id, new_type):

        spots = self.__parking_lot.get_spots()

        for index, spot in enumerate(spots):
            if spot.get_spot_id() == spot_id:

                if spot.is_occupied():
                    raise InvalidSpotError(
                        f"Cannot edit spot {spot_id}: it is currently occupied."
                    )

                # Replace the whole spot with a new one of the new type,
                # using only the public constructor (no private access)
                spots[index] = ParkingSpot(spot_id, new_type)
                return True

        raise InvalidSpotError(f"Spot {spot_id} does not exist.")

    # ==========================================
    # Search & Sort
    # ==========================================

    def search_by_plate(self, plate):

        if plate not in self.__vehicles:
            raise VehicleNotFoundError(f"No vehicle with plate '{plate}'.")

        return self.__vehicles[plate]

    def search_by_type(self, vehicle_type):

        return [
            v for v in self.__vehicles.values()
            if v.get_vehicle_type() == vehicle_type
        ]

    def sort_by_entry_time(self):

        return sorted(
            self.__vehicles.values(),
            key=lambda v: v.get_entry_time()
        )

    def sort_by_cost(self, descending=True):

        return sorted(
            self.__vehicles.values(),
            key=lambda v: v.calculate_cost(),
            reverse=descending
        )

    # ==========================================
    # JSON persistence
    # ==========================================

    def save_to_json(self, filename):

        try:
            data = {"spots": []}

            for spot in self.__parking_lot.get_spots():
                spot_data = {
                    "spot_id": spot.get_spot_id(),
                    "spot_type": spot.get_spot_type(),
                    "vehicle": None
                }

                if spot.is_occupied():
                    v = spot.get_vehicle()
                    spot_data["vehicle"] = {
                        "type": v.get_vehicle_type(),
                        "plate": v.get_license_plate(),
                        "entry_time": str(v.get_entry_time())
                    }

                data["spots"].append(spot_data)

            with open(filename, "w") as f:
                json.dump(data, f, indent=4)

            return True

        except (OSError, TypeError) as e:
            raise DataFileError(f"Could not save to '{filename}': {e}")

    def load_from_json(self, filename):

        try:
            with open(filename, "r") as f:
                data = json.load(f)

        except FileNotFoundError:
            raise DataFileError(f"File '{filename}' was not found.")
        except json.JSONDecodeError:
            raise DataFileError(f"File '{filename}' contains invalid JSON.")

        try:
            for spot_data in data["spots"]:

                # Look for an existing spot with this id
                spot = None
                for existing_spot in self.__parking_lot.get_spots():
                    if existing_spot.get_spot_id() == spot_data["spot_id"]:
                        spot = existing_spot
                        break

                # If it doesn't exist yet, create and add it
                if spot is None:
                    spot = ParkingSpot(spot_data["spot_id"], spot_data["spot_type"])
                    self.__parking_lot.add_spot(spot)

                vehicle_data = spot_data.get("vehicle")

                if vehicle_data:
                    vehicle_class = self.VEHICLE_CLASSES.get(vehicle_data["type"])

                    if vehicle_class is None:
                        raise DataFileError(
                            f"Unknown vehicle type '{vehicle_data['type']}'."
                        )

                    vehicle = vehicle_class(vehicle_data["plate"])
                    vehicle.enter()

                    spot.park_vehicle(vehicle)

                    self.__vehicles[vehicle.get_license_plate()] = vehicle
                    self.__active_plates.add(vehicle.get_license_plate())

            return True

        except KeyError as e:
            raise DataFileError(f"Malformed data in '{filename}': missing {e}")

    # ==========================================
    # CSV export
    # ==========================================

    def export_log_to_csv(self, filename):

        try:
            with open(filename, "w", newline="") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["action", "plate", "type", "time", "cost"]
                )
                writer.writeheader()

                for entry in self.__transaction_log:
                    writer.writerow(entry)

            return True

        except OSError as e:
            raise DataFileError(f"Could not write CSV file '{filename}': {e}")

    # Read a transaction log back from a CSV file
    def load_log_from_csv(self, filename):

        try:
            loaded_log = []

            with open(filename, "r", newline="") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    loaded_log.append(row)

            self.__transaction_log = loaded_log

            return loaded_log

        except FileNotFoundError:
            raise DataFileError(f"File '{filename}' was not found.")
        except csv.Error as e:
            raise DataFileError(f"Could not read CSV file '{filename}': {e}")