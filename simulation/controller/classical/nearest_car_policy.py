from simulation.core.elevator_system import ElevatorSystem


def nearest_car_policy(elevator_system: ElevatorSystem):
    """
    Naiwny algorytm 'Nearest Car' (ulepszony):
    - Jeśli winda ma pasażerów, obsługuje ich docelowe piętra.
    - Jeśli winda jest pusta, jedzie do najbliższych wezwań (może mieć wiele przypisanych).
    - Rozstrzyga remisy wybierając windę stojącą albo z mniejszym obciążeniem.
    Zwraca listę akcji: ["UP", "DOWN", "STANDING", ...].
    """

    actions = ["STANDING"] * len(elevator_system.elevators)

    # --- krok 1: przypisanie wezwań do wind ---
    assignments = {i: [] for i in range(len(elevator_system.elevators))}

    for floor in elevator_system.requested_floors:
        nearest_idx = None
        nearest_dist = float("inf")

        for i, elevator in enumerate(elevator_system.elevators):
            # jeśli winda ma pasażerów → nadal można jej przypisać wezwanie
            # (ale obsłuży je dopiero po wysadzeniu pasażerów)
            dist = abs(elevator.current_floor - floor)

            if dist < nearest_dist:
                nearest_dist = dist
                nearest_idx = i
            elif dist == nearest_dist:
                # rozstrzyganie remisu: preferuj STANDING lub mniej pasażerów
                if elevator.state == "STANDING":
                    nearest_idx = i
                elif (nearest_idx is not None and
                      elevator.people_inside_int < elevator_system.elevators[nearest_idx].people_inside_int):
                    nearest_idx = i

        if nearest_idx is not None:
            assignments[nearest_idx].append(floor)

    # --- krok 2: decyzja dla każdej windy ---
    for i, elevator in enumerate(elevator_system.elevators):

        target = None

        # priorytet: najpierw pasażerowie w środku
        if elevator.chosen_floors:
            target = min(elevator.chosen_floors, key=lambda f: abs(f - elevator.current_floor))

        # jeśli brak pasażerów → bierz wezwanie z kolejki przypisań
        elif assignments[i]:
            target = min(assignments[i], key=lambda f: abs(f - elevator.current_floor))

        if target is None:
            actions[i] = "STANDING"
        elif target > elevator.current_floor:
            actions[i] = "UP"
        elif target < elevator.current_floor:
            actions[i] = "DOWN"
        else:
            actions[i] = "STANDING"  # na piętrze → obsługa

    return actions
