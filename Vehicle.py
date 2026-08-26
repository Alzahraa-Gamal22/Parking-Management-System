from datetime import datetime
class Vehicle:
    def __init__(self, license_plate):
        self.__license_plate = license_plate
        self.__entry_time = None
        self.__exit_time = None

    # Getter
    def get_license_plate(self):
        return self.__license_plate

    def get_entry_time(self):
        return self.__entry_time

    def get_exit_time(self):
        return self.__exit_time


    # Entry
    def enter(self, entry_time=None):
        self.__entry_time = entry_time or datetime.now()

    # Exit
    def exit(self, exit_time=None):
        self.__exit_time = exit_time or datetime.now()

    
    # Calculate parking duration
    def get_duration_hours(self):
        if self.__entry_time is None:
            return 0

        end_time = self.__exit_time

        if end_time is None:
            end_time = datetime.now()

        duration = end_time - self.__entry_time

        return duration.total_seconds() / 3600

    # Polymorphism
    def calculate_cost(self):
        return 0

    def get_vehicle_type(self):
        return "Vehicle"

    def __str__(self):
        return f"{self.get_vehicle_type()} - {self.__license_plate}"
