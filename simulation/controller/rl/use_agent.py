from simulation.training.models.q_learning_agent import QLearningAgent
from simulation.core.elevator_system import ElevatorSystem


class AgentController:
    def __init__(self, model_path):
        self.agent = QLearningAgent.load(model_path)

    def use_agent(self, elevator_system: ElevatorSystem):
        """
        Używa wytrenowanego agenta do sterowania windą.
        Zwraca listę akcji np. ["UP"].
        """
        state = self.agent.get_state(elevator_system)
        action_idx = self.agent.choose_action(state)
        return [self.agent.actions[action_idx]]
