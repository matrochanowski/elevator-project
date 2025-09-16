from simulation import config

from simulation.controller.classical.nearest_car_policy import nearest_car_policy

from simulation.core.elevator_system import ElevatorSystem
from simulation.core.elevator import Elevator

from simulation.engine.step_operator import operator

ALGORITHM = nearest_car_policy

config = config.load_config()

FLOORS = 5
MAX_PEOPLE_FLOOR = 10
DELAY = 4
MAX_PEOPLE_ELEVATOR = 5


def run_simulation(steps: int, system: ElevatorSystem):
    i = 0
    while i < steps:
        action = ALGORITHM(system)
        _, system, _ = operator(action, system)
        i += 1
        print(action)


building = ElevatorSystem(config["floors"], 10, config["max_people_floor"], config["delay"])
building.elevators = [
    Elevator(config["max_people_elevator"], config["floors"]),
    Elevator(config["max_people_elevator"], config["floors"])
]
run_simulation(config["steps"], building)
