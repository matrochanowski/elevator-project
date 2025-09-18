from simulation.engine.utils import *

from simulation.core.elevator_system import ElevatorSystem

import random


def operator(actions, elevator_system: ElevatorSystem):
    def increase_personal_counter_elevator(elevator):
        for passenger_inside in elevator.people_inside_arr:
            passenger_inside.increase_waiting_time()

    def increase_personal_counter_floors():
        for floor in elevator_system.people_array:
            for passenger_outside in floor:
                if passenger_outside is not None:
                    passenger_outside.increase_waiting_time()

    def apply_actions_to_elevators(elevator_list, acts):
        for i, elv in enumerate(elevator_list):
            action = acts[i]

            if elv.delay > 0:
                continue  # Elevator is currently delayed

            if action == "UP":
                elv.state_up()
                floor_up(elv)

            elif action == "DOWN":
                elv.state_down()
                floor_down(elv)

            elif action == "STANDING":
                elv.state_none()

    # --- wykonanie akcji ---
    apply_actions_to_elevators(elevator_system.elevators, actions)

    # --- sprawdź drzwi i obsłuż pasażerów dla każdej windy ---
    for lift in elevator_system.elevators:
        if lift.state == "STANDING" and lift.delay == 0:
            if lift.decide_if_stop(elevator_system):
                visiting_floor(
                    lift.current_floor,
                    lift,
                    elevator_system
                )

    # --- obsłuż spawn pasażerów ---
    new_floors_arr = []
    if random.randint(0, elevator_system.spawn_chance) == 1:
        new_floors_arr = generate_passengers(
            elevator_system.max_floor,
            elevator_system.max_people_floor,
            elevator_system.people_array,
        )
    for new_floor in new_floors_arr:
        if new_floor not in elevator_system.requested_floors:
            elevator_system.add_floor_to_requested_queue(new_floor)

    # --- aktualizacja ludzi w windach ---
    for lift in elevator_system.elevators:
        lift.update_people_inside()

    # --- zwiększanie czasu oczekiwania ---
    for lift in elevator_system.elevators:
        increase_personal_counter_elevator(lift)
    increase_personal_counter_floors()

    # --- zmniejszanie delay ---
    for lift in elevator_system.elevators:
        if lift.delay > 0:
            lift.delay -= 1

    # --- wektor stanu systemu ---
    vector_state = get_system_state(elevator_system.elevators, elevator_system)

    return elevator_system.elevators, elevator_system, vector_state
