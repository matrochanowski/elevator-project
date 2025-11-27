from simulation.training.agents.q_learning_agent import QLearningAgent, QLearningAgentsGroup
from simulation.training.scripts.utils import get_state
from simulation.core.elevator_system import ElevatorSystem


class AgentsGroupController:
    def __init__(self, model_path):
        try:
            group = QLearningAgentsGroup.load(model_path)
            self.agents = group.agents
        except Exception as e:
            print(e)
            agent = QLearningAgent.load(model_path)
            self.agents = [agent]

    def use_agents(self, elevator_system: ElevatorSystem):
        state = get_state(elevator_system)

        if len(self.agents) == 1:
            idx = self.agents[0].choose_action(state)
            return [self.agents[0].actions[idx]]

        actions = []
        for i, agent in enumerate(self.agents):
            if elevator_system.elevators[i].delay == 0:
                idx = agent.choose_action(state)
                actions.append(agent.actions[idx])
            else:
                actions.append("STANDING")

        return actions
