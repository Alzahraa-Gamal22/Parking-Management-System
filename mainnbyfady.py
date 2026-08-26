from Vehicle import Vehicle
from Car import Car
from Motorcycle import Motorcycle
from Truck import Truck

from parkingspot import ParkingSpot
from Parkinglot import ParkingLot

from DataManager import DataManager
from exceptions import (
    DuplicateVehicleError,
    VehicleNotFoundError,
    InvalidSpotError,
    DataFileError
)


def main():

    print("=" * 50)
    print("       PARKING MANAGEMENT SYSTEM")
    print("=" * 50)

    # ==========================================
    # 1. Create Parking Lot + DataManager
    # ==========================================

    parking_lot = ParkingLot("Main Parking")
    data_manager = DataManager(parking_lot)

    print("\nParking Lot Created Successfully!")
    print("Name: Main Parking")

    # ==========================================
    # 2. Create Parking Spots
    # ==========================================

    parking_lot.add_spot(ParkingSpot(1, "Regular"))
    parking_lot.add_spot(ParkingSpot(2, "Regular"))
    parking_lot.add_spot(ParkingSpot(3, "Regular"))
    parking_lot.add_spot(ParkingSpot(4, "Large"))
    parking_lot.add_spot(ParkingSpot(5, "Large"))

    print("\n5 Parking Spots Added Successfully!")

    # ==========================================
    # 3. Create Vehicles
    # ==========================================

    car = Car("ABC-123")
    motorcycle = Motorcycle("MOTO-555")
    truck = Truck("TRUCK-999")

    print("\nVehicles Created:")
    print("-----------------------------")
    print(f"1. {car.get_vehicle_type()} - {car.get_license_plate()}")
    print(f"2. {motorcycle.get_vehicle_type()} - {motorcycle.get_license_plate()}")
    print(f"3. {truck.get_vehicle_type()} - {truck.get_license_plate()}")

    # ==========================================
    # 4. Vehicle Entry (through DataManager now)
    # ==========================================

    print("\n")
    print("=" * 50)
    print("          VEHICLE ENTRY")
    print("=" * 50)

    for vehicle in [car, motorcycle, truck]:
        try:
            data_manager.add_vehicle(vehicle)
        except (DuplicateVehicleError, InvalidSpotError) as e:
            print(f"Error: {e}")

    # ==========================================
    # 5. Display Parking Status
    # ==========================================

    print("\n")
    print("=" * 50)
    print("          PARKING STATUS")
    print("=" * 50)

    parking_lot.display_parking_status()

    # ==========================================
    # 6. Test Duplicate Vehicle (through DataManager)
    # ==========================================

    print("\n")
    print("=" * 50)
    print("       DUPLICATE VEHICLE TEST")
    print("=" * 50)

    try:
        data_manager.add_vehicle(car)
    except DuplicateVehicleError as e:
        print(f"Error: {e}")

    # ==========================================
    # 7. Search & Sort demo
    # ==========================================

    print("\n")
    print("=" * 50)
    print("          SEARCH & SORT")
    print("=" * 50)

    found = data_manager.search_by_plate("MOTO-555")
    print(f"Found by plate: {found}")

    trucks = data_manager.search_by_type("Truck")
    print(f"Trucks currently parked: {[str(t) for t in trucks]}")

    by_cost = data_manager.sort_by_cost()
    print("Sorted by cost (highest first):")
    for v in by_cost:
        print(f"  {v} -> {v.calculate_cost():.2f} EGP")

    # ==========================================
    # 8. Vehicle Exit (through DataManager)
    # ==========================================

    print("\n")
    print("=" * 50)
    print("          VEHICLE EXIT")
    print("=" * 50)

    try:
        cost = data_manager.delete_vehicle("ABC-123")
        print(f"Vehicle exited. Cost: {cost:.2f} EGP")
    except VehicleNotFoundError as e:
        print(f"Error: {e}")

    # ==========================================
    # 9. Display Status After Exit
    # ==========================================

    print("\n")
    print("=" * 50)
    print("     PARKING STATUS AFTER EXIT")
    print("=" * 50)

    parking_lot.display_parking_status()

    # ==========================================
    # 10. Test Invalid Vehicle (through DataManager)
    # ==========================================

    print("\n")
    print("=" * 50)
    print("       INVALID VEHICLE TEST")
    print("=" * 50)

    try:
        data_manager.delete_vehicle("NOT-FOUND")
    except VehicleNotFoundError as e:
        print(f"Error: {e}")

    # ==========================================
    # 11. JSON save/load demo
    # ==========================================

    print("\n")
    print("=" * 50)
    print("          JSON SAVE / LOAD")
    print("=" * 50)

    try:
        data_manager.save_to_json("parking_data.json")
        print("Parking state saved to parking_data.json")
    except DataFileError as e:
        print(f"Error: {e}")

    # ==========================================
    # 12. CSV export demo
    # ==========================================

    print("\n")
    print("=" * 50)
    print("          CSV EXPORT")
    print("=" * 50)

    try:
        data_manager.export_log_to_csv("transaction_log.csv")
        print("Transaction log exported to transaction_log.csv")
    except DataFileError as e:
        print(f"Error: {e}")

    # ==========================================
    # 13. Finish
    # ==========================================

    print("\n")
    print("=" * 50)
    print("       SYSTEM TEST COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    main()