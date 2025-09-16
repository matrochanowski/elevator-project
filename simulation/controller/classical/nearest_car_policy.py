def nearest_car_policy(elevator_system):
    """
    Prosty algorytm 'Nearest Car' (minimum distance).
    Przydziela wezwania (requested_floors) do najbliższej windy.
    Zwraca listę akcji (["UP", "DOWN", "STANDING", ...]) dla wszystkich wind.
    """

    # Początkowo każda winda "nic nie robi"
    actions = ["STANDING"] * len(elevator_system.elevators)

    if not elevator_system.requested_floors:
        return actions

    # Słownik: winda -> docelowe piętro
    assignments = {i: None for i in range(len(elevator_system.elevators))}

    for floor in elevator_system.requested_floors:
        # znajdź windę najbliższą danemu piętru
        nearest_idx = None
        nearest_dist = float("inf")

        for i, elevator in enumerate(elevator_system.elevators):
            dist = abs(elevator.current_floor - floor)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_idx = i

        # przypisz piętro do najbliższej windy
        assignments[nearest_idx] = floor

    # ustal akcje dla każdej windy
    for i, elevator in enumerate(elevator_system.elevators):
        target = assignments[i]
        if target is None:
            continue

        if target > elevator.current_floor:
            actions[i] = "UP"
        elif target < elevator.current_floor:
            actions[i] = "DOWN"
        else:
            actions[i] = "STANDING"  # już na piętrze → np. otwieranie drzwi

    return actions
