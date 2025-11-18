import random
import copy
import csv
from pathlib import Path
import os
from collections import defaultdict

from simulation.core.person import Person
from simulation.core.elevator_system import ElevatorSystem
from simulation.config import load_config
from simulation.schema import ConfigSchema
from simulation.enums import TrafficGeneratorEnum

CONFIG: ConfigSchema = load_config()

ENGINE_DIR = Path(__file__).resolve().parents[0]
SCENARIO_DIR = ENGINE_DIR / "scenarios"

if CONFIG.traffic.generator_type is TrafficGeneratorEnum('from file'):
    filename = CONFIG.traffic.from_file_params.filename
    scenario_by_step = defaultdict(list)
    with open(os.path.join(SCENARIO_DIR, filename), 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            s = int(row['step'])
            scenario_by_step[s].append(row)


# ------------------ helper functions ------------------

def should_generate_passengers(config: ConfigSchema, step: int) -> bool:
    """Decides whether to generate passengers in this simulation step."""
    if config.traffic.seed is not None:
        random.seed(config.traffic.seed + step)

    intensity = config.traffic.intensity
    if intensity <= 0:
        return False

    rand_threshold = 1 / intensity
    return random.random() < (1 / rand_threshold)


def generate_amount(config: ConfigSchema) -> int:
    """Determines how many passengers appear in this step."""
    return max(1, int(round(random.expovariate(1.0 / config.traffic.intensity))))


def normalize_distribution(dist: list[float], expected_len: int, name: str) -> list[float]:
    """Validates and normalizes a floor probability distribution."""
    if len(dist) != expected_len:
        raise ValueError(f"{name} must have length {expected_len}, but got {len(dist)}.")
    total = sum(dist)
    if total <= 0:
        raise ValueError(f"{name} must have positive weights.")
    return [x / total for x in dist]


def insert_person(people_array, start_floor: int, person: Person, max_people_floor: int):
    """Inserts a person object into the first available slot on a given floor."""
    for i in range(max_people_floor):
        if people_array[start_floor, i] is None:
            people_array[start_floor, i] = copy.deepcopy(person)
            break


# ------------------ main generation dispatcher ------------------

def generate_passengers(elevator_system: ElevatorSystem, step: int):
    config: ConfigSchema = CONFIG
    generator_type = config.traffic.generator_type

    match generator_type:
        case TrafficGeneratorEnum('up-peak'):
            return generate_up_peak(elevator_system, step, config)
        case TrafficGeneratorEnum('down-peak'):
            return generate_down_peak(elevator_system, step, config)
        case TrafficGeneratorEnum('mixed-peak'):
            return generate_mixed_peak(elevator_system, step, config)
        case TrafficGeneratorEnum('from file'):
            print("test 1")
            return generate_from_file(elevator_system, step, config)
    return []


# --------------- apriori generator --------------

def generate_scenario_apriori(n_steps: int, scenario_name: str):
    config: ConfigSchema = CONFIG

    fake_system = ElevatorSystem(config.floors, config.max_people_floor)

    scenario = []

    for step in range(n_steps):
        generate_passengers(fake_system, step)
        pair = 0

        for floor in fake_system.people_array:
            for person in floor:
                person: Person | None
                if person:
                    scenario.append((step, pair, person.starting_floor, person.desired_floor))
                    pair += 1

        fake_system = ElevatorSystem(config.floors, config.max_people_floor)

    path = f'{os.path.join(SCENARIO_DIR, scenario_name)}.csv'
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['step', 'pair_number', 'starting_floor', 'desired_floor'])
        writer.writerows(scenario)


# ------------------ generators ------------------

def generate_up_peak(elevator_system: ElevatorSystem, step: int, config: ConfigSchema):
    people_array = elevator_system.people_array
    max_floor = elevator_system.max_floor
    max_people_floor = elevator_system.max_people_floor

    params = config.traffic.up_peak_params
    if params is None or not should_generate_passengers(config, step):
        return []

    amount = generate_amount(config)
    starting_floor = params.arrival_floor
    new_floors_arr = []

    dist = None
    if params.destination_distribution is not None:
        dist = normalize_distribution(params.destination_distribution, max_floor + 1, "destination_distribution")

    for _ in range(amount):
        desired_floor = random.choices(range(max_floor + 1), weights=dist, k=1)[0] if dist else random.randint(0,
                                                                                                               max_floor)
        if desired_floor == starting_floor:
            continue

        person = Person(step=step, starting_floor=starting_floor, desired_floor=desired_floor)
        if starting_floor not in new_floors_arr:
            new_floors_arr.append(starting_floor)
        insert_person(people_array, starting_floor, person, max_people_floor)

    return new_floors_arr


def generate_down_peak(elevator_system: ElevatorSystem, step: int, config: ConfigSchema):
    people_array = elevator_system.people_array
    max_floor = elevator_system.max_floor
    max_people_floor = elevator_system.max_people_floor

    params = config.traffic.down_peak_params
    if params is None or not should_generate_passengers(config, step):
        return []

    amount = generate_amount(config)
    destination_floor = params.destination_floor
    new_floors_arr = []

    dist = None
    if params.origin_distribution is not None:
        dist = normalize_distribution(params.origin_distribution, max_floor + 1, "origin_distribution")

    for _ in range(amount):
        starting_floor = random.choices(range(max_floor + 1), weights=dist, k=1)[0] if dist else random.randint(0,
                                                                                                                max_floor)
        if starting_floor == destination_floor:
            continue

        person = Person(step=step, starting_floor=starting_floor, desired_floor=destination_floor)
        if starting_floor not in new_floors_arr:
            new_floors_arr.append(starting_floor)
        insert_person(people_array, starting_floor, person, max_people_floor)

    return new_floors_arr


def generate_mixed_peak(elevator_system: ElevatorSystem, step: int, config: ConfigSchema):
    people_array = elevator_system.people_array
    max_floor = elevator_system.max_floor
    max_people_floor = elevator_system.max_people_floor

    params = config.traffic.mixed_peak_params
    if params is None or not should_generate_passengers(config, step):
        return []

    amount = generate_amount(config)
    new_floors_arr = []

    ratios = {
        "up": params.up_peak_ratio,
        "down": params.down_peak_ratio,
        "inter": params.interfloor_ratio
    }

    categories = random.choices(
        population=["up", "down", "inter"],
        weights=[ratios["up"], ratios["down"], ratios["inter"]],
        k=amount
    )

    for cat in categories:
        if cat == "up":
            starting_floor = params.arrival_floor
            desired_floor = random.randint(starting_floor + 1, max_floor)
            if desired_floor == starting_floor:
                continue

        elif cat == "down":
            starting_floor = random.randint(1, max_floor)
            if starting_floor == params.destination_floor:
                continue
            desired_floor = params.destination_floor

        else:  # interfloor
            start = random.randint(0, max_floor)
            dest = random.randint(0, max_floor)
            if start == dest:
                continue
            starting_floor = start
            desired_floor = dest

        person = Person(step=step, starting_floor=starting_floor, desired_floor=desired_floor)
        if starting_floor not in new_floors_arr:
            new_floors_arr.append(starting_floor)
        insert_person(people_array, starting_floor, person, max_people_floor)

    return new_floors_arr


def generate_from_file(elevator_system: ElevatorSystem, step: int, config: ConfigSchema):
    new_floors_arr = []
    if step in scenario_by_step.keys():
        for pair in scenario_by_step[step]:
            starting_floor = int(pair['starting_floor'])
            desired_floor = int(pair['desired_floor'])
            person = Person(starting_floor=starting_floor, desired_floor=desired_floor, step=step)
            if starting_floor not in new_floors_arr:
                new_floors_arr.append(starting_floor)
            insert_person(elevator_system.people_array, starting_floor, person, config.max_people_floor)
    print(new_floors_arr)
    return new_floors_arr
