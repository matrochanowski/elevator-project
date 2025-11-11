from simulation.core.elevator import Elevator
from simulation.core.elevator_system import ElevatorSystem
from simulation.core.person import Person
import numpy as np
from typing import List, Set, Tuple
from datetime import datetime
import os
import pandas as pd


def visiting_floor(floor_int, elevator: Elevator, elevator_system: ElevatorSystem):
    """
    Execute actions when stopping at a floor
    :param floor_int: Current floor
    :param elevator: Elevator class object
    :param elevator_system: ElevatorSystem class object
    :return:
    """
    people_array, passengers_at_dest = elevator_system.people_array, elevator_system.passengers_at_dest

    # --- PASSENGERS LEAVING ---
    passengers_inside_arr = elevator.people_inside_arr
    passengers_leaving_arr = []
    for passenger_inside in passengers_inside_arr:
        if passenger_inside.desired_floor == floor_int:
            passengers_leaving_arr.append(passenger_inside)
    elevator.leave(passengers_leaving_arr)
    for passenger_left in passengers_leaving_arr:
        passengers_at_dest.append(passenger_left)

    # --- PASSENGERS GETTING IN ---
    floor = people_array[floor_int]
    sorted_floor = sort_passengers(floor)
    space_left = elevator.how_much_space_left()
    passengers_entering_arr = []
    for i in range(min(space_left, len(sorted_floor))):
        if sorted_floor[i] is not None:
            passengers_entering_arr.append(sorted_floor[i])

    if passengers_entering_arr:
        elevator_system.remove_floor_from_requested(floor_int)

    elevator.enter(passengers_entering_arr)

    # deleting boarded passengers from the floor
    for passenger in people_array[floor_int]:
        if passenger in passengers_entering_arr:
            people_array[people_array == passenger] = None

    elevator.delay += elevator.time_at_floor


def how_much_passengers_floor(floor_int, people_array):
    """
    Policz pasażerów na piętrze
    :param floor_int: Aktualne piętro
    :param people_array: Macierz numpy o wymiarach liczba piętra x maksymalna ilość osób w piętrze
    :return:
    """
    count_int = 0
    for passenger in people_array[floor_int]:
        if passenger is not None:
            count_int += 1
    return count_int


def sort_passengers(passengers_array):
    """
    Posortuj pasażerów od najdłużej do najkrócej czekających
    :param passengers_array: Macierz numpy o wymiarach liczba piętra x maksymalna ilość osób w piętrze
    :return:
    """
    # układ: pasażerowie czekający najdłużej od lewej strony wektora
    return sorted(filter(lambda x: x is not None, passengers_array), key=lambda person: person.journey_time,
                  reverse=True)


def how_many_people(people_array, elevators: List[Elevator]):
    people = 0
    for floor in people_array:
        for person in floor:
            if person is not None:
                people += 1
    for elevator in elevators:
        for person in elevator.people_inside_arr:
            if person is not None:
                people += 1

    return people


def get_system_state(
        elevators: List[Elevator],
        elevator_system: ElevatorSystem) -> np.ndarray:
    """
    Encode the state of a multi-elevator system for reinforcement learning.

    Each Elevator_i_State is a vector of size (1 + F + 1) and contains:
      * Normalized scalar of current floor: current_floor / max_floor
      * Binary vector indicating floors requested from inside the elevator (size F)
      * Scalar representing the elevator's direction: -1 (DOWN), 0 (STANDING), +1 (UP)

    Global_Outside_Requests is a binary vector of size F.

    Final state vector shape: E * (F + 2) + F
    """
    E = len(elevators)
    F = elevator_system.max_floor + 1

    sub_states = []
    for elev in elevators:
        # Normalized current floor as scalar
        current_floor_norm = np.array([elev.current_floor / (F - 1)], dtype=np.float32)

        # Binary vector of inside-chosen floors
        inside_reqs = np.zeros(F, dtype=np.float32)
        for f in elev.chosen_floors:
            inside_reqs[f] = 1.0

        # Direction: map state string to numeric
        dir_map = {"DOWN": -1.0, "STANDING": 0.0, "UP": 1.0}
        direction = dir_map.get(elev.state, 0.0)
        direction_vec = np.array([direction], dtype=np.float32)

        # Concatenate scalar floor, inside_reqs, direction
        sub_states.append(np.concatenate([current_floor_norm, inside_reqs, direction_vec]))

    # Global outside requests
    outside_reqs = np.zeros(F, dtype=np.float32)
    for f in elevator_system.requested_floors:
        outside_reqs[f] = 1.0

    return np.concatenate(sub_states + [outside_reqs])


def unpack_state(
        s: np.ndarray,
        E: int,
        F: int
) -> Tuple[List[int], List[Set[int]], List[int], Set[int]]:
    """
    Unpacks the 1D state vector `s` into meaningful components.

    Vector shape: E * (F + 2) + F

    Returns:
      - curr_floors: list of int, current floor (denormalized)
      - inside_reqs: list of sets of ints
      - directions: list of int (-1, 0, 1)
      - outside_reqs: set of ints
    """
    curr_floors = []
    inside_reqs = []
    directions = []
    offset = 0

    for _ in range(E):
        # Normalized floor (scalar)
        norm_floor = s[offset]
        floor = int(round(norm_floor * (F - 1)))
        curr_floors.append(floor)
        offset += 1

        # Inside requests (size F)
        in_vec = s[offset: offset + F]
        inside_set = set(np.nonzero(in_vec)[0].tolist())
        inside_reqs.append(inside_set)
        offset += F

        # Direction (size 1)
        direction = int(np.round(s[offset]))
        directions.append(direction)
        offset += 1

    # Outside requests (size F)
    out_vec = s[offset: offset + F]
    outside_reqs = set(np.nonzero(out_vec)[0].tolist())

    return curr_floors, inside_reqs, directions, outside_reqs


def int_to_action(action_int):
    """
    Transforms a single integer (0-8) representing a combined action
    for two lifts into a tuple of their states.

    The integer is decoded assuming base-3 representation where:
    index = action_int // 3 (for lift 1)
    index = action_int % 3 (for lift 2)
    And indices map to states: 0='UP', 1='DOWN', 2='STANDING'.

    Args:
        action_int (int): An integer from 0 to 8 representing the
                          combined action.

    Returns:
        tuple: A tuple of two strings, where the first element is the state
               of the first lift ('UP', 'DOWN', or 'STANDING') and the second
               element is the state of the second lift.

    Raises:
        ValueError: If the input integer is outside the valid range [0, 8].
    """
    if not isinstance(action_int, int) or not (0 <= action_int <= 8):
        raise ValueError("Input action_int must be an integer between 0 and 8.")

    # Mapping from index (0, 1, 2) to state string ('UP', 'DOWN', 'STANDING')
    lift_states_map = ['UP', 'DOWN', 'STANDING']

    # Decode the integer to get the state indices for each lift
    lift1_state_index = action_int // 3
    lift2_state_index = action_int % 3

    # Get the state strings using the indices
    lift1_state = lift_states_map[lift1_state_index]
    lift2_state = lift_states_map[lift2_state_index]

    return (lift1_state, lift2_state)


simulation_log = []
run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


def log_simulation_step(step_idx: int, elevator_system):
    """Saves one simulation step to global list simulation_log"""
    global simulation_log

    for elv_id, elv in enumerate(elevator_system.elevators):
        record = {
            "step": step_idx,
            "elevator_id": elv_id,
            "floor": elv.current_floor,
            "state": elv.state,
            "delay": elv.delay,
            "num_inside": len(elv.people_inside_arr),
            "requested_floors": len(elevator_system.requested_floors),
            "waiting_total": sum(len(f) for f in elevator_system.people_array),
        }
        simulation_log.append(record)


def save_simulation_log(output_dir="logs", filename_prefix="run"):
    """Saves logs to Parquet format"""
    global simulation_log, run_timestamp

    if not simulation_log:
        return

    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{filename_prefix}_{run_timestamp}.parquet")

    df = pd.DataFrame(simulation_log)
    df.to_parquet(filename, index=False, compression="snappy")

    print(f"[LOG] Saved {len(df)} lines to file: {filename}")


def summarize_simulation(elevator_system: ElevatorSystem):
    passengers: List[Person] = elevator_system.passengers_at_dest
    n_passengers = len(passengers)

    if not passengers:
        print("No passengers at destination, no data to summarize")
        return

    mean_journey_time = 0
    mean_j_time_dist = 0
    mean_waiting_time = 0
    mean_travel_time = 0
    for passenger in passengers:
        mean_journey_time += passenger.journey_time
        mean_j_time_dist += passenger.journey_time / abs(passenger.starting_floor - passenger.desired_floor)
        mean_waiting_time += passenger.waiting_time
        mean_travel_time += passenger.travel_time

    mean_journey_time /= n_passengers
    mean_waiting_time /= n_passengers
    mean_travel_time /= n_passengers
    mean_j_time_dist /= n_passengers

    print("Średnia długość całkowitej podróży: ", mean_journey_time)
    print("Średnia długość oczekiwania na przybycie windy: ", mean_waiting_time)
    print("Średnia długość podróży windą: ", mean_travel_time)
    print("Średnia długość całkowitej podróży na piętro: ", mean_j_time_dist)
