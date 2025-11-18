from enum import Enum
from typing import List, Optional
import os
from pathlib import Path
from pydantic import BaseModel, Field, model_validator

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class AlgorithmEnum(str, Enum):
    Q_LEARNING = "q_learning"
    NEAREST_CAR = "nearest_car"
    COLLECTIVE_CONTROL = "collective_control"

    @property
    def pretty(self) -> str:
        mapping = {
            AlgorithmEnum.Q_LEARNING: "Q-Learning",
            AlgorithmEnum.NEAREST_CAR: "Nearest Car",
            AlgorithmEnum.COLLECTIVE_CONTROL: "Collective Control"
        }
        return mapping[self]

    @property
    def needs_model(self) -> bool:
        if self in AlgorithmEnum.Q_LEARNING:
            return True
        return False

    def get_controller(self, model=None):
        match self:
            case AlgorithmEnum.NEAREST_CAR:
                from simulation.controller.classical.nearest_car_policy import nearest_car_policy
                return nearest_car_policy
            case AlgorithmEnum.COLLECTIVE_CONTROL:
                from simulation.controller.classical.collective_control_policy import collective_control_policy
                return collective_control_policy
            case AlgorithmEnum.Q_LEARNING:
                from simulation.controller.rl.agent_controller import AgentController
                model_path = os.path.join(PROJECT_ROOT, "simulation", "controller", "rl", "models", self.value, model)
                agent = AgentController(model_path)
                return agent.use_agent
            case _:
                return None

    def list_models(self) -> List[str]:
        if not self.needs_model:
            return []

        models_dir = os.path.join(
            PROJECT_ROOT, "simulation", "controller", "rl", "models", self.value
        )
        if not os.path.exists(models_dir):
            return []

        return [
            f for f in os.listdir(models_dir)
            if f.endswith(".pkl")
        ]


class TrafficGeneratorEnum(str, Enum):
    UP_PEAK = "up-peak"
    DOWN_PEAK = "down-peak"
    INTERFLOOR = "interfloor"
    MIXED_PEAK = "mixed-peak"
    UNIFORM = "uniform"
    FROM_FILE = "from file"


class UpPeakParams(BaseModel):
    arrival_floor: int = Field(default=0,
                               description="Floor, where passengers start their journey")
    destination_distribution: Optional[List[float]] = Field(
        default=None,
        description="Distribution of target floors (if None, uniform)"
    )


class DownPeakParams(BaseModel):
    destination_floor: int = Field(default=0, description="Target floor")
    origin_distribution: Optional[List[float]] = Field(
        default=None,
        description="Distribution of starting floors (if None, uniform)"
    )


class InterfloorParams(BaseModel):
    origin_destination_matrix: Optional[List[List[float]]] = Field(
        default=None,
        description="Probability matrix of flows between floors [from][to]"
    )
    symmetric_traffic: bool = Field(default=True, description="Is the flow symmetrical")


class MixedPeakParams(BaseModel):
    destination_floor: int = Field(default=0, description="Target floor for down-peak")
    arrival_floor: int = Field(default=0,
                               description="Floor, where passengers start their journey for up-peak")
    up_peak_ratio: float = Field(default=0.45, ge=0, le=1, description="Proportion of up-peak")
    down_peak_ratio: float = Field(default=0.45, ge=0, le=1, description="Proportion of down-peak")
    interfloor_ratio: float = Field(default=0.10, ge=0, le=1, description="Proportion of interfloor")

    @model_validator(mode='after')
    def validate_ratios(self):
        total = self.up_peak_ratio + self.down_peak_ratio + self.interfloor_ratio
        if not abs(total - 1.0) < 0.001:
            raise ValueError("Sum of proportions must equal 1.0")
        return self


class UniformParams(BaseModel):
    origin_distribution: Optional[List[float]] = Field(
        default=None,
        description="Distribution of starting floors (if None, uniform)"
    )
    destination_distribution: Optional[List[float]] = Field(
        default=None,
        description="Distribution of target floors (if None, uniform)"
    )


class FromFileParams(BaseModel):
    filename: str = Field(description="Filename of the generated scenario")
