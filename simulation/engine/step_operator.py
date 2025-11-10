from simulation.engine.utils import *
from simulation.engine.traffic_generator import *

from simulation.core.elevator_system import ElevatorSystem


def operator(actions, elevator_system: ElevatorSystem, step: int):
    def increase_personal_counter_elevator(elevator):
        for passenger_inside in elevator.people_inside_arr:
            passenger_inside.increase_waiting_time()

    def increase_personal_counter_floors():
        for floor in elevator_system.people_array:
            for passenger_outside in floor:
                if passenger_outside is not None:
                    passenger_outside.increase_waiting_time()

    def apply_actions_to_elevators(elevator_list: List[Elevator], acts):
        for i, elv in enumerate(elevator_list):
            action = acts[i]

            if elv.delay > 0:
                continue  # Elevator is currently delayed

            if action == "UP":
                if elv.state != "UP":
                    elv.current_acc = 0
                elv.state_up()
                elv.increase_floor()

            elif action == "DOWN":
                if elv.state != "DOWN":
                    elv.current_acc = 0
                elv.state_down()
                elv.decrease_floor()

            elif action == "STANDING":
                elv.state_none()

    # --- taking an action ---
    apply_actions_to_elevators(elevator_system.elevators, actions)

    # --- check doors and serve passengers ---
    for lift in elevator_system.elevators:
        if lift.state == "STANDING" and lift.delay == 0:
            if lift.decide_if_stop(elevator_system):
                visiting_floor(
                    lift.current_floor,
                    lift,
                    elevator_system
                )

    # --- serve passengers spawning ---
    new_floors_arr = generate_passengers(elevator_system, step)
    for new_floor in new_floors_arr:
        if new_floor not in elevator_system.requested_floors:
            elevator_system.add_floor_to_requested_queue(new_floor)

    # --- update people in elevators ---
    for lift in elevator_system.elevators:
        lift.update_people_inside()

    # --- increase waiting time ---
    for lift in elevator_system.elevators:
        increase_personal_counter_elevator(lift)
    increase_personal_counter_floors()

    # --- decrease delay ---
    for lift in elevator_system.elevators:
        if lift.delay > 0:
            lift.delay -= 1

    # --- state vector (deprecated) ---
    vector_state = get_system_state(elevator_system.elevators, elevator_system)

    return elevator_system.elevators, elevator_system, vector_state
