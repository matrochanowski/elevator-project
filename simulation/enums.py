from enum import Enum
from typing import List
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class AlgorithmEnum(str, Enum):
    Q_LEARNING = "q_learning"
    NEAREST_CAR = "nearest_car"

    @property
    def pretty(self) -> str:
        mapping = {
            AlgorithmEnum.Q_LEARNING: "Q-Learning",
            AlgorithmEnum.NEAREST_CAR: "Nearest Car"
        }
        return mapping[self]

    @property
    def needs_model(self) -> bool:
        return self in {AlgorithmEnum.Q_LEARNING}

    def get_controller(self, model=None):
        match self:
            case AlgorithmEnum.NEAREST_CAR:
                from simulation.controller.classical.nearest_car_policy import nearest_car_policy
                return nearest_car_policy
            case AlgorithmEnum.Q_LEARNING:
                from simulation.controller.rl.agent_controller import AgentController
                model_path = os.path.join(PROJECT_ROOT, "simulation", "controller", "rl", "models", self.value, model)
                print(model_path)
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
