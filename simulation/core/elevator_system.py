import numpy as np


class ElevatorSystem:
    def __init__(self, max_floor, spawn_chance, max_people_per_floor):
        self.max_floor = max_floor
        self.spawn_chance = spawn_chance
        self.max_people_floor = max_people_per_floor

        self.elevators = []  # lista obiektów Elevator
        self.people_array = np.full((max_floor + 1, self.max_people_floor), None, dtype=object)
        self.passengers_at_dest = []  # lista pasażerów, którzy dotarli do celu
        self.requested_floors = []  # piętra "wezwane" do obsługi

    def __str__(self):
        info = [f"ElevatorSystem status:", f"Max floor: {self.max_floor}", f"Requested floors: {self.requested_floors}",
                f"Passengers at destination: {len(self.passengers_at_dest)}", "Elevators:"]
        for i, elevator in enumerate(self.elevators):
            info.append(
                f"  Elevator {i}: Floor {elevator.current_floor}, Chosen floors: {elevator.chosen_floors}, Passengers: {len(elevator.people_inside_arr)}")
        info.append("People waiting on floors:")
        for floor in range(self.max_floor + 1):
            waiting = [p for p in self.people_array[floor] if p is not None]
            if waiting:
                info.append(f"  Floor {floor}: {len(waiting)} people waiting")
        return "\n".join(info)

    def add_elevator(self, elevator):
        self.elevators.append(elevator)

    def add_floor_to_requested_queue(self, new_floor):
        if new_floor not in self.requested_floors:
            self.requested_floors.append(new_floor)

    def remove_floor_from_requested(self, floor):
        if floor in self.requested_floors:
            self.requested_floors.remove(floor)

    def requested_chosen_floors_above(self, elevator):
        current_floor = elevator.current_floor
        return [f for f in self.requested_floors + elevator.chosen_floors if f > current_floor]

    def requested_chosen_floors_below(self, elevator):
        current_floor = elevator.current_floor
        return [f for f in self.requested_floors + elevator.chosen_floors if f < current_floor]
