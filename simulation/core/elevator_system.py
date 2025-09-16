import numpy as np


class ElevatorSystem:
    def __init__(self, max_floor, spawn_chance, max_people_per_floor, opening_door_delay):
        self.max_floor = max_floor
        self.spawn_chance = spawn_chance
        self.max_people_floor = max_people_per_floor
        self.opening_door_delay = opening_door_delay

        self.elevators = []  # lista obiektów Elevator
        self.people_array = np.full((max_floor + 1, self.max_people_floor), None, dtype=object)
        self.passengers_at_dest = []  # lista pasażerów, którzy dotarli do celu
        self.requested_floors = []  # piętra "wezwane" do obsługi

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
