import random
from datetime import datetime, timedelta

from Car import Car
from Motorcycle import Motorcycle
from Truck import Truck


class ParkingSimulation:

    def __init__(self, data_manager, parking_lot):
        self.data_manager = data_manager
        self.parking_lot = parking_lot

        # Simulated clock
        self.current_time = None

        # Vehicles currently inside
        self.active_vehicles = {}

        # Scheduled exit times
        self.scheduled_exits = {}

        # Statistics
        self.total_entries = 0
        self.successful_entries = 0
        self.failed_entries = 0
        self.total_exits = 0
        self.total_revenue = 0

        # Event history
        self.event_log = []

        # Occupancy history
        self.occupancy_history = []

        # Used to generate unique license plates
        self.vehicle_counter = 1000

    # ==========================================
    # Generate Random Vehicle
    # ==========================================

    def generate_vehicle(self):

        vehicle_type = random.choices(
            ["Car", "Motorcycle", "Truck"],
            weights=[60, 30, 10]
        )[0]

        self.vehicle_counter += 1

        license_plate = f"SIM-{self.vehicle_counter}"

        if vehicle_type == "Car":
            return Car(license_plate)

        elif vehicle_type == "Motorcycle":
            return Motorcycle(license_plate)

        else:
            return Truck(license_plate)

    # ==========================================
    # Generate Random Parking Duration
    # ==========================================

    def generate_parking_duration(self, vehicle):

        vehicle_type = vehicle.get_vehicle_type()

        if vehicle_type == "Car":
            return random.randint(1, 5)

        elif vehicle_type == "Motorcycle":
            return random.randint(1, 4)

        elif vehicle_type == "Truck":
            return random.randint(2, 6)

        return 1

    # ==========================================
    # Simulate Vehicle Entry
    # ==========================================

    def simulate_entry(self):

        vehicle = self.generate_vehicle()

        self.total_entries += 1

        try:
            success = self.data_manager.add_vehicle(
                vehicle,
                self.current_time
            )

            if success:

                self.successful_entries += 1

                plate = vehicle.get_license_plate()

                # Store active vehicle
                self.active_vehicles[plate] = vehicle

                # Generate random parking duration
                duration = self.generate_parking_duration(vehicle)

                # Calculate when vehicle should leave
                exit_time = (
                    self.current_time
                    + timedelta(hours=duration)
                )

                self.scheduled_exits[plate] = exit_time

                # Record event
                self.event_log.append({
                    "time": self.current_time,
                    "action": "entry",
                    "plate": plate,
                    "type": vehicle.get_vehicle_type(),
                    "duration": duration
                })

                print(
                    f"[{self.current_time.strftime('%H:%M')}] "
                    f"{vehicle.get_vehicle_type()} "
                    f"{plate} ENTERED "
                    f"(stays {duration}h)"
                )

        except Exception as e:

            self.failed_entries += 1

            print(
                f"[{self.current_time.strftime('%H:%M')}] "
                f"Entry failed: {e}"
            )

    # ==========================================
    # Simulate Vehicle Exit
    # ==========================================

    def simulate_exit(self, plate):

        if plate not in self.active_vehicles:
            return

        try:

            # Delete vehicle through DataManager
            cost = self.data_manager.delete_vehicle(
                plate,
                self.current_time
            )

            vehicle = self.active_vehicles[plate]

            self.total_exits += 1
            self.total_revenue += cost

            duration = vehicle.get_duration_hours()

            # Record exit event
            self.event_log.append({
                "time": self.current_time,
                "action": "exit",
                "plate": plate,
                "type": vehicle.get_vehicle_type(),
                "duration": duration,
                "cost": cost
            })

            print(
                f"[{self.current_time.strftime('%H:%M')}] "
                f"{vehicle.get_vehicle_type()} "
                f"{plate} EXITED "
                f"(duration {duration:.2f}h, "
                f"cost {cost:.2f} EGP)"
            )

            # Remove from active vehicles
            del self.active_vehicles[plate]
            del self.scheduled_exits[plate]

        except Exception as e:

            print(
                f"[{self.current_time.strftime('%H:%M')}] "
                f"Exit failed: {e}"
            )

    # ==========================================
    # Process Vehicles That Should Exit
    # ==========================================

    def process_exits(self):

        vehicles_to_exit = []

        for plate, exit_time in self.scheduled_exits.items():

            if self.current_time >= exit_time:
                vehicles_to_exit.append(plate)

        for plate in vehicles_to_exit:
            self.simulate_exit(plate)

    # ==========================================
    # Calculate Occupancy
    # ==========================================

    def calculate_occupancy(self):

        spots = self.parking_lot.get_spots()

        total_spots = len(spots)

        if total_spots == 0:
            return 0

        occupied_spots = sum(
            1
            for spot in spots
            if spot.is_occupied()
        )

        return (occupied_spots / total_spots) * 100

    # ==========================================
    # Record Occupancy
    # ==========================================

    def record_occupancy(self):

        spots = self.parking_lot.get_spots()

        total_spots = len(spots)

        occupied_spots = sum(
            1
            for spot in spots
            if spot.is_occupied()
        )

        available_spots = total_spots - occupied_spots

        occupancy = 0

        if total_spots > 0:
            occupancy = (
                occupied_spots / total_spots
            ) * 100

        self.occupancy_history.append({
            "time": self.current_time,
            "occupied": occupied_spots,
            "available": available_spots,
            "occupancy": occupancy
        })

    # ==========================================
    # Generate Random Arrivals
    # ==========================================

    def generate_arrivals(self):

        hour = self.current_time.hour

        # Morning rush
        if 8 <= hour <= 10:
            number_of_arrivals = random.randint(1, 3)

        # Evening rush
        elif 16 <= hour <= 19:
            number_of_arrivals = random.randint(1, 4)

        # Normal daytime
        elif 11 <= hour <= 15:
            number_of_arrivals = random.randint(0, 2)

        # Night
        else:
            number_of_arrivals = random.randint(0, 1)

        for _ in range(number_of_arrivals):
            self.simulate_entry()

    # ==========================================
    # Run Simulation
    # ==========================================

    def run(self, start_time=None, duration_hours=24):

        if start_time is None:

            start_time = datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

        self.current_time = start_time

        end_time = (
            start_time
            + timedelta(hours=duration_hours)
        )

        print("\n")
        print("=" * 55)
        print("              PARKING SIMULATION")
        print("=" * 55)
        print(f"Start time: {start_time}")
        print(f"Duration:   {duration_hours} hours")
        print("=" * 55)

        # Simulation moves every 15 minutes
        time_step = timedelta(minutes=15)

        while self.current_time < end_time:

            # Vehicles whose parking time ended leave first
            self.process_exits()

            # Generate new arrivals
            self.generate_arrivals()

            # Record parking occupancy
            self.record_occupancy()

            # Move simulated clock forward
            self.current_time += time_step

        print("\n")
        print("=" * 55)
        print("             SIMULATION FINISHED")
        print("=" * 55)

        self.print_statistics()

        return self.get_statistics()

    # ==========================================
    # Statistics
    # ==========================================

    def get_statistics(self):

        if self.occupancy_history:

            average_occupancy = (
                sum(
                    item["occupancy"]
                    for item in self.occupancy_history
                )
                / len(self.occupancy_history)
            )

            maximum_occupancy = max(
                item["occupancy"]
                for item in self.occupancy_history
            )

        else:

            average_occupancy = 0
            maximum_occupancy = 0

        return {
            "total_entries": self.total_entries,
            "successful_entries": self.successful_entries,
            "failed_entries": self.failed_entries,
            "total_exits": self.total_exits,
            "total_revenue": self.total_revenue,
            "average_occupancy": average_occupancy,
            "maximum_occupancy": maximum_occupancy
        }

    # ==========================================
    # Print Statistics
    # ==========================================

    def print_statistics(self):

        stats = self.get_statistics()

        print("\n========== SIMULATION STATISTICS ==========")

        print(
            f"Total vehicles generated: "
            f"{stats['total_entries']}"
        )

        print(
            f"Successful entries: "
            f"{stats['successful_entries']}"
        )

        print(
            f"Failed entries: "
            f"{stats['failed_entries']}"
        )

        print(
            f"Total exits: "
            f"{stats['total_exits']}"
        )

        print(
            f"Total revenue: "
            f"{stats['total_revenue']:.2f} EGP"
        )

        print(
            f"Average occupancy: "
            f"{stats['average_occupancy']:.2f}%"
        )

        print(
            f"Maximum occupancy: "
            f"{stats['maximum_occupancy']:.2f}%"
        )

        print("============================================")

    # ==========================================
    # Get Event Log
    # ==========================================

    def get_event_log(self):

        return self.event_log

    # ==========================================
    # Get Occupancy History
    # ==========================================

    def get_occupancy_history(self):

        return self.occupancy_history