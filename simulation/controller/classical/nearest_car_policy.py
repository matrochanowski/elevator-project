from simulation.core.elevator_system import ElevatorSystem


def nearest_car_policy(elevator_system: ElevatorSystem):
    """
    Naive 'Nearest Car' Algorithm:
    - If the elevator has passengers, it serves their destination floors.
    - If the elevator is empty, it goes to the nearest calls (it can have multiple calls).
    - Breaks ties by choosing the standing elevator or the one with the least load.

    Returns a list of actions: ["UP", "DOWN", "STANDING", ...].
    """

    actions = ["STANDING"] * len(elevator_system.elevators)

    assignments = {i: [] for i in range(len(elevator_system.elevators))}

    for floor in elevator_system.requested_floors:
        nearest_idx = None
        nearest_dist = float("inf")

        for i, elevator in enumerate(elevator_system.elevators):
            dist = abs(elevator.current_floor - floor)

            if dist < nearest_dist:
                nearest_dist = dist
                nearest_idx = i
            elif dist == nearest_dist:
                if elevator.state == "STANDING":
                    nearest_idx = i
                elif (nearest_idx is not None and
                      elevator.people_inside_int < elevator_system.elevators[nearest_idx].people_inside_int):
                    nearest_idx = i

        if nearest_idx is not None:
            assignments[nearest_idx].append(floor)

    for i, elevator in enumerate(elevator_system.elevators):

        target = None

        if elevator.chosen_floors:
            target = min(elevator.chosen_floors, key=lambda f: abs(f - elevator.current_floor))

        elif assignments[i]:
            target = min(assignments[i], key=lambda f: abs(f - elevator.current_floor))

        if target is None:
            actions[i] = "STANDING"
        elif target > elevator.current_floor:
            actions[i] = "UP"
        elif target < elevator.current_floor:
            actions[i] = "DOWN"
        else:
            actions[i] = "STANDING"

    return actions
