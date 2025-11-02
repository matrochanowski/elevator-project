import numpy as np

from simulation.core.elevator_system import ElevatorSystem
from .schema import ElevatorSystemState, ElevatorState


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

    # --- część dla każdej windy ---
    for elevator in system.elevators:
        # Pozycja windy (one-hot)
        floors = np.zeros(system.max_floor + 1, dtype=int)
        floors[elevator.current_floor] = 1
        state.extend(floors.tolist())

        # Wybrane piętra w środku windy (binarne)
        chosen = np.zeros(system.max_floor + 1, dtype=int)
        for f in elevator.chosen_floors:
            if 0 <= f <= system.max_floor:
                chosen[f] = 1
        state.extend(chosen.tolist())

        # Kierunek windy (-1, 0, 1)
        if elevator.state == "UP":
            direction = 1
        elif elevator.state == "DOWN":
            direction = -1
        else:
            direction = 0
        state.append(direction)

    # --- część globalna: przyciski wezwań z zewnątrz ---
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
        # Pozycja windy
        position = state[idx: idx + n_floors]
        current_floor = int(np.argmax(position))
        idx += n_floors

        # Wybrane piętra
        chosen = state[idx: idx + n_floors]
        chosen_floors = [i for i, v in enumerate(chosen) if v == 1]
        idx += n_floors

        # Kierunek
        direction = int(state[idx])
        idx += 1

        elevators.append(ElevatorState(
            current_floor=current_floor,
            chosen_floors=chosen_floors,
            direction=direction
        ))

    # Zewnętrzne wezwania
    external_calls = state[idx: idx + n_floors]
    external_floors = [i for i, v in enumerate(external_calls) if v == 1]

    return ElevatorSystemState(
        elevators=elevators,
        external_calls=external_floors
    )


def reward_function(prev_state: ElevatorSystemState,
                    next_state: ElevatorSystemState,
                    action: list) -> float:
    """
    Oblicza nagrodę dla systemu wind.

    Zasady:
    1. +1 za każde zewnętrzne wezwanie, które zniknęło (pasażer odebrany)
    2. +1 za każde wewnętrzne wezwanie, które zniknęło (pasażer wysadzony)
    3. Kara -10 jeśli winda próbuje jechać poza zakres budynku
    4. Nagroda za ruch w kierunku zgłoszeń: 1/distance do najbliższego zgłoszenia w danym kierunku
    """
    reward = 0.0
    n_elevators = len(prev_state.elevators)
    max_floor = max(prev_state.elevators[0].current_floor, *(e.current_floor for e in
                                                             prev_state.elevators))  # zakładamy, że wszystkie windy w tym samym system.max_floor

    # --- 1. Odebrani pasażerowie (zewnętrzne wezwania) ---
    prev_external = set(prev_state.external_calls)
    next_external = set(next_state.external_calls)
    removed_external = prev_external - next_external
    reward += len(removed_external) * 10

    # --- 2. Wysadzeni pasażerowie (wewnętrzne zgłoszenia) ---
    for prev_e, next_e in zip(prev_state.elevators, next_state.elevators):
        removed_internal = set(prev_e.chosen_floors) - set(next_e.chosen_floors)
        reward += len(removed_internal) * 10

    # --- 3. Ruch zgodny z akcją i kierunkiem zgłoszeń ---
    for i, (prev_e, act) in enumerate(zip(prev_state.elevators, action)):
        floor = prev_e.current_floor
        max_f = max_floor

        # --- sprawdzenie najbliższego zgłoszenia w danym kierunku ---
        targets = set(prev_e.chosen_floors) | set(prev_state.external_calls)

        if not targets:
            continue  # brak zgłoszeń, brak dodatkowej nagrody

        if act == "UP":
            higher_targets = [f for f in targets if f > floor]
            if higher_targets:
                distance = min(higher_targets) - floor
                reward += 5.0 / distance
        elif act == "DOWN":
            lower_targets = [f for f in targets if f < floor]
            if lower_targets:
                distance = floor - max(lower_targets)
                reward += 5.0 / distance
        # STANDING → brak dodatkowej nagrody

    return reward
