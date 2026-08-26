from Parkinglot import ParkingLot
from parkingspot import ParkingSpot

from DataManager import DataManager
from Simulation import ParkingSimulation


def main():

    # Create parking lot
    parking_lot = ParkingLot("Simulation Parking")

    # Create parking spots
    for i in range(1, 11):
        if i <= 7:
            parking_lot.add_spot(
                ParkingSpot(i, "Regular")
            )
        else:
            parking_lot.add_spot(
                ParkingSpot(i, "Large")
            )

    # Create DataManager
    data_manager = DataManager(parking_lot)

    # Create simulation
    simulation = ParkingSimulation(
        data_manager,
        parking_lot
    )

    # Run 24-hour simulation
    statistics = simulation.run(
        duration_hours=24
    )

    print("\nFinal Statistics:")
    print(statistics)


if __name__ == "__main__":
    main()