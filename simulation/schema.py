from pydantic import BaseModel, Field, model_validator
from typing import List, Optional

from simulation.enums import (AlgorithmEnum, TrafficGeneratorEnum, UpPeakParams,
                              DownPeakParams, InterfloorParams, MixedPeakParams,
                              UniformParams)


class TrafficConfigSchema(BaseModel):
    generator_type: TrafficGeneratorEnum
    intensity: float = Field(ge=0, description="Mean passengers number per step")
    seed: int | None

    # Parameters specific for generator type
    up_peak_params: Optional[UpPeakParams] = None
    down_peak_params: Optional[DownPeakParams] = None
    interfloor_params: Optional[InterfloorParams] = None
    mixed_peak_params: Optional[MixedPeakParams] = None
    uniform_params: Optional[UniformParams] = None

    @model_validator(mode='after')
    def validate_generator_params(self):
        generator_type = self.generator_type

        required_params = {
            TrafficGeneratorEnum.UP_PEAK: self.up_peak_params,
            TrafficGeneratorEnum.DOWN_PEAK: self.down_peak_params,
            TrafficGeneratorEnum.INTERFLOOR: self.interfloor_params,
            TrafficGeneratorEnum.MIXED_PEAK: self.mixed_peak_params,
            TrafficGeneratorEnum.UNIFORM: self.uniform_params
        }

        if required_params[generator_type] is None:
            return self

        return self


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
    algorithm: AlgorithmEnum
    model: str | None = None
    traffic: TrafficConfigSchema
