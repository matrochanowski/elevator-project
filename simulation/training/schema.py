from pydantic import BaseModel
from typing import Optional


class QLearningParamsSchema(BaseModel):
    alpha: float
    gamma: float
    starting_epsilon: float
    epsilon_decay: float


class TrainingConfigSchema(BaseModel):
    algorithm: str
    save_name: str
    episodes: int
    q_learning_params: Optional[QLearningParamsSchema] = None
