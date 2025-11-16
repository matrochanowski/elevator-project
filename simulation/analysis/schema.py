from pydantic import BaseModel

from simulation.schema import ConfigSchema


class Results(BaseModel):
    mean_journey_time: float
    mean_waiting_time: float
    mean_travel_time: float
    mean_j_time_dist: float
    n_passengers: int


class ResultsInfoForGui(BaseModel):
    info: ConfigSchema
    results: Results
