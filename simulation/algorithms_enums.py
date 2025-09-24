from enum import Enum


class Algorithm(str, Enum):
    Q_LEARNING = "q_learning"
    NEAREST_CAR = "nearest_car"

    @property
    def pretty(self) -> str:
        mapping = {
            Algorithm.Q_LEARNING: "Q-Learning",
            Algorithm.NEAREST_CAR: "Nearest Car"
        }
        return mapping[self]

    def get_controller(self):
        if self is Algorithm.NEAREST_CAR:
            from simulation.controller.classical.nearest_car_policy import nearest_car_policy
            return nearest_car_policy
        elif self is Algorithm.Q_LEARNING:
            from simulation.controller.rl.use_agent import AgentController
            agent = AgentController("")  # TODO load correct algorithm
            return agent.use_agent
        return None
