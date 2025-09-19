from pydantic import BaseModel
from typing import List


class ElevatorConfigSchema(BaseModel):
    max_people: int
    speed: int
    starting_floor: int


class ConfigSchema(BaseModel):
    floors: int
    max_people_floor: int
    steps: int
    visualisation: bool
    elevators: List[ElevatorConfigSchema]
