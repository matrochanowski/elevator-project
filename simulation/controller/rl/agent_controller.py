from simulation.training.agents.q_learning_agent import QLearningAgent
from simulation.training.scripts.utils import get_state
from simulation.core.elevator_system import ElevatorSystem


class AgentController:
    def __init__(self, model_path):
        self.agent = QLearningAgent.load(model_path, alpha=0.1, gamma=0.95, epsilon=0.05)

    def use_agent(self, elevator_system: ElevatorSystem):
        """
        Używa wytrenowanego agenta do sterowania windą.
        Zwraca listę akcji np. ["UP"].
        """
        state = get_state(elevator_system)
        action_idx = self.agent.choose_action(state)
        return [self.agent.actions[action_idx]]
