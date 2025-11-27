import numpy as np

from simulation.core.elevator_system import ElevatorSystem
from .schema import ElevatorSystemState, ElevatorState

from simulation.training.config import load_training_config


TRAINING_CONFIG = load_training_config()

def get_state(system: ElevatorSystem):
    """
    Stan opisany binarnie:
    - dla każdej windy:
        [binarne położenie windy] (np. dla 3 pięter i windy na 1: [0,1,0])
        [binarne wybrane piętra w środku windy] (np. [1,0,0])
        [kierunek windy] (-1, 0, 1)
    - po wszystkich windach:
        [binarne przyciski wezwań z zewnątrz]
    """
    state = []

    for elevator in system.elevators:
        floors = np.zeros(system.max_floor + 1, dtype=int)
        floors[elevator.current_floor] = 1
        state.extend(floors.tolist())

        chosen = np.zeros(system.max_floor + 1, dtype=int)
        for f in elevator.chosen_floors:
            if 0 <= f <= system.max_floor:
                chosen[f] = 1
        state.extend(chosen.tolist())

        if elevator.state == "UP":
            direction = 1
        elif elevator.state == "DOWN":
            direction = -1
        else:
            direction = 0
        state.append(direction)

    external_calls = np.zeros(system.max_floor + 1, dtype=int)
    for f in system.requested_floors:
        if 0 <= f <= system.max_floor:
            external_calls[f] = 1
    state.extend(external_calls.tolist())

    return tuple(state)


def decode_state(state, system: ElevatorSystem) -> ElevatorSystemState:
    """
    Odszyfrowuje stan zwrócony przez get_state().
    Zwraca obiekt ElevatorSystemState.
    """
    max_floor = system.max_floor
    n_floors = max_floor + 1
    n_elevators = len(system.elevators)

    state = list(state)
    idx = 0
    elevators = []

    for _ in range(n_elevators):
        # Elevator position
        position = state[idx: idx + n_floors]
        current_floor = int(np.argmax(position))
        idx += n_floors

        # Chosen floors
        chosen = state[idx: idx + n_floors]
        chosen_floors = [i for i, v in enumerate(chosen) if v == 1]
        idx += n_floors

        # Directions
        direction = int(state[idx])
        idx += 1

        elevators.append(ElevatorState(
            current_floor=current_floor,
            chosen_floors=chosen_floors,
            direction=direction
        ))

    # Outside calls
    external_calls = state[idx: idx + n_floors]
    external_floors = [i for i, v in enumerate(external_calls) if v == 1]

    return ElevatorSystemState(
        elevators=elevators,
        external_calls=external_floors
    )


def reward_function(prev_state: ElevatorSystemState,
                    next_state: ElevatorSystemState,
                    action: list) -> float:
    reward_params = TRAINING_CONFIG.reward_params
    reward = 0.0

    # === reward: pick-up ===
    prev_external = set(prev_state.external_calls)
    next_external = set(next_state.external_calls)
    removed_external = prev_external - next_external
    reward += len(removed_external) * 10 * reward_params.reward_pick_up

    # === reward: delivery ===
    for prev_e, next_e in zip(prev_state.elevators, next_state.elevators):
        removed_internal = set(prev_e.chosen_floors) - set(next_e.chosen_floors)
        reward += len(removed_internal) * 10 * reward_params.reward_delivery

    # === penalty: people waiting outside ===
    # liczba pięter, na których ktoś czeka
    n_waiting_outside = len(next_state.external_calls)
    reward -= n_waiting_outside * reward_params.penalty_outside

    # === penalty: people inside elevators ===
    n_inside = sum(len(e.chosen_floors) for e in next_state.elevators)
    reward -= n_inside * reward_params.penalty_inside

    return reward

