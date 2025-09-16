from utils import *
import random


def operator(actions, max_floor, spawn_chance, max_people_floor,
             people_array, winda, winda2, elevators, passengers_at_dest,
             opening_door_delay, elevator_system, algorithm='classical'):
    def increase_personal_counter_elevator(elevator):
        for passenger_inside in elevator.people_inside_arr:
            passenger_inside.increase_waiting_time()

    def increase_personal_counter_floors():
        for floor in people_array:
            for passenger_outside in floor:
                if passenger_outside is not None:
                    passenger_outside.increase_waiting_time()

    def apply_actions_to_elevators(elevator_list, actions):
        """
        Given a list of elevators and a list of actions (e.g., ["UP", "STANDING"]),
        apply the movement logic based on the action.
        """
        for i, lift in enumerate(elevator_list):
            action = actions[i]

            if lift.delay > 0:
                continue  # Elevator is currently delayed, skip its turn

            if action == "UP":
                lift.state_up()
                floor_up(lift)

            elif action == "DOWN":
                lift.state_down()
                floor_down(lift)

            elif action == "STANDING":
                lift.state_none()

    apply_actions_to_elevators(elevators, actions)

    # ----- sprawdź czy otworzyć drzwi windy -----
    if winda.state == 'STANDING' and winda.delay == 0:
        if winda.decide_if_stop(elevator_system):
            visiting_floor(winda.current_floor, winda, people_array, passengers_at_dest, opening_door_delay)
    if winda2.state == 'STANDING' and winda2.delay == 0:
        if winda2.decide_if_stop(elevator_system):
            visiting_floor(winda2.current_floor, winda2, people_array, passengers_at_dest, opening_door_delay)

    current_floor = winda.current_floor
    manage_requests(current_floor, elevator_system, people_array)
    current_state = winda.state
    requested_floors = elevator_system.requested_floors

    # ----- zewnętrzne operacje pasażerów -----
    new_floors_arr = []
    if random.randint(0, spawn_chance) == 1:  # 1 / spawn_chance szansy na jakichś pasażerów w turze
        new_floors_arr = generate_passengers(max_floor, max_people_floor, people_array)
    for new_floor in new_floors_arr:
        if new_floor not in requested_floors:
            elevator_system.add_floor_to_requested_queue(new_floor)  # wciskanie przycisków żądania windy
    winda.update_people_inside()
    winda2.update_people_inside()

    manage_requests(current_floor, elevator_system, people_array)
    # ----- zwiększanie czasu oczekiwania wszystkich osób w systemie -----
    increase_personal_counter_elevator(winda)
    increase_personal_counter_elevator(winda2)
    increase_personal_counter_floors()

    if winda.delay > 0:
        winda.delay -= 1
    if winda2.delay > 0:
        winda2.delay -= 1

    vector_state = get_system_state(list(elevators), elevator_system)

    return elevators, elevator_system, vector_state
