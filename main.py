from Vehicle import Vehicle
from Car import Car
from Motorcycle import Motorcycle
from Truck import Truck

from parkingspot import ParkingSpot
from Parkinglot import ParkingLot


def main():

    print("=" * 50)
    print("       PARKING MANAGEMENT SYSTEM")
    print("=" * 50)

    # ==========================================
    # 1. Create Parking Lot
    # ==========================================

    parking_lot = ParkingLot("Main Parking")

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
    # 4. Vehicle Entry
    # ==========================================

    print("\n")
    print("=" * 50)
    print("          VEHICLE ENTRY")
    print("=" * 50)

    parking_lot.vehicle_entry(car)
    parking_lot.vehicle_entry(motorcycle)
    parking_lot.vehicle_entry(truck)

    # ==========================================
    # 5. Display Parking Status
    # ==========================================

    print("\n")
    print("=" * 50)
    print("          PARKING STATUS")
    print("=" * 50)

    parking_lot.display_parking_status()

    # ==========================================
    # 6. Test Duplicate Vehicle
    # ==========================================

    print("\n")
    print("=" * 50)
    print("       DUPLICATE VEHICLE TEST")
    print("=" * 50)

    parking_lot.vehicle_entry(car)

    # ==========================================
    # 7. Vehicle Exit
    # ==========================================

    print("\n")
    print("=" * 50)
    print("          VEHICLE EXIT")
    print("=" * 50)

    parking_lot.vehicle_exit("ABC-123")

    # ==========================================
    # 8. Display Status After Exit
    # ==========================================

    print("\n")
    print("=" * 50)
    print("     PARKING STATUS AFTER EXIT")
    print("=" * 50)

    parking_lot.display_parking_status()

    # ==========================================
    # 9. Test Invalid Vehicle
    # ==========================================

    print("\n")
    print("=" * 50)
    print("       INVALID VEHICLE TEST")
    print("=" * 50)

    parking_lot.vehicle_exit("NOT-FOUND")

    # ==========================================
    # 10. Finish
    # ==========================================

    print("\n")
    print("=" * 50)
    print("       SYSTEM TEST COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    main()