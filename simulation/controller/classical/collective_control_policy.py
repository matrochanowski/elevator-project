from simulation.core.elevator_system import ElevatorSystem

def collective_control_policy(elevator_system: ElevatorSystem):
    """
    Collective Control Heuristic (with stop-on-floor check):
    - Elevator stops if it is on a floor with passengers to pick up or drop off.
    - Otherwise continues in current direction if there are requests.
    - Changes direction only if no requests remain in the current direction.
    - If standing, chooses direction based on nearest request.
    """
    actions = ["STANDING"] * len(elevator_system.elevators)

    for i, elevator in enumerate(elevator_system.elevators):
        current_floor = elevator.current_floor
        direction = elevator.state

        if elevator.people_inside_int >= elevator.max_people_inside:
            targets = set(elevator.chosen_floors)
        else:
            targets = set(elevator.chosen_floors).union(elevator_system.requested_floors)

        if current_floor in targets:
            actions[i] = "STANDING"
            continue

        if not targets:
            actions[i] = "STANDING"
            continue

        above = [f for f in targets if f > current_floor]
        below = [f for f in targets if f < current_floor]

        if direction == "UP":
            actions[i] = "UP" if above else ("DOWN" if below else "STANDING")
        elif direction == "DOWN":
            actions[i] = "DOWN" if below else ("UP" if above else "STANDING")
        else:
            if above and below:
                nearest_above = min(above) - current_floor
                nearest_below = current_floor - max(below)
                actions[i] = "UP" if nearest_above <= nearest_below else "DOWN"
            elif above:
                actions[i] = "UP"
            elif below:
                actions[i] = "DOWN"
            else:
                actions[i] = "STANDING"

    return actions
