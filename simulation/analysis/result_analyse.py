from simulation.core.person import Person
from simulation.core.elevator_system import ElevatorSystem
from simulation.config import ConfigSchema

from simulation.analysis.schema import Results, ResultsInfoForGui

from typing import List
import pickle

from pathlib import Path
import os

REPO_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = REPO_DIR / "database" / "logs"


def analyse_from_file(filename: str) -> ResultsInfoForGui:
    with open(os.path.join(LOG_DIR, filename), "rb") as file:
        data = pickle.load(file)

    system: ElevatorSystem = data['system']
    config: ConfigSchema = data['config']

    results = summarize_simulation(system)

    return ResultsInfoForGui(info=config, results=results)


def summarize_simulation(elevator_system: ElevatorSystem):
    passengers: List[Person] = elevator_system.passengers_at_dest
    n_passengers = len(passengers)

    if not passengers:
        raise ValueError("No passengers at destination")

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

    results = Results(
        mean_waiting_time=mean_waiting_time,
        mean_journey_time=mean_journey_time,
        mean_travel_time=mean_travel_time,
        mean_j_time_dist=mean_j_time_dist,
        n_passengers=n_passengers
    )

    print("Średnia długość całkowitej podróży: ", mean_journey_time)
    print("Średnia długość oczekiwania na przybycie windy: ", mean_waiting_time)
    print("Średnia długość podróży windą: ", mean_travel_time)
    print("Średnia długość całkowitej podróży na piętro: ", mean_j_time_dist)

    return results
