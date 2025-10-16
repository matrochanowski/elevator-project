from typing import List
from pydantic import BaseModel


class ElevatorState(BaseModel):
    """Simplified state of a single elevator"""
    current_floor: int
    chosen_floors: List[int]
    direction: int


class ElevatorSystemState(BaseModel):
    """Simplified state of elevator system"""
    elevators: List[ElevatorState]
    external_calls: List[int]
