from pydantic import BaseModel
from typing import Optional


class QLearningParamsSchema(BaseModel):
    alpha: float
    gamma: float
    starting_epsilon: float
    epsilon_decay: float

class RewardMultipliersSchema(BaseModel):
    penalty_outside: float
    penalty_inside: float
    reward_pick_up: float
    reward_delivery: float


class TrainingConfigSchema(BaseModel):
    algorithm: str
    save_name: str
    episodes: int
    steps_per_episode: int
    q_learning_params: Optional[QLearningParamsSchema] = None
    reward_params: RewardMultipliersSchema
