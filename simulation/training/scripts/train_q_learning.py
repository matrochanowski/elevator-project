from simulation import config
from simulation.core.elevator import Elevator
from simulation.core.elevator import ElevatorSystem
from simulation.engine.step_operator import operator
from simulation.training.agents.q_learning_agent import QLearningAgent, QLearningAgentsGroup
from simulation.training.scripts.utils import *

from typing import Tuple
import matplotlib.pyplot as plt
import numpy as np

cfg = config.load_config()

ACTIONS = ["UP", "DOWN", "STANDING"]


def train_q_learning(episodes=100,
                     steps=200,
                     agents_group: QLearningAgentsGroup = None) -> Tuple[QLearningAgentsGroup, float]:
    if agents_group is None:
        raise ValueError("No agents passed.")

    agents = agents_group.agents
    whole_reward = 0

    for ep in range(episodes):
        system = ElevatorSystem(cfg.floors, cfg.max_people_floor)
        system.elevators = [
            Elevator(max_people_inside=e.max_people,
                     max_possible_floor=cfg.floors,
                     speed=e.speed)
            for e in cfg.elevators
        ]

        if len(agents) != len(system.elevators):
            raise ValueError("Number of agents must equal number of elevators.")

        state = get_state(system)
        reward_sum = 0

        for step in range(steps):
            flags = [el.delay == 0 for el in system.elevators]

            action_indices = [
                agents[i].choose_action(state) if flags[i] else None
                for i in range(len(agents))
            ]

            actions = [
                ACTIONS[action_indices[i]] if flags[i] else "STANDING"
                for i in range(len(agents))
            ]

            state_before = get_state(system)
            system = operator(actions, system, step=step)
            state_after = get_state(system)

            reward = reward_function(
                decode_state(state_before, system),
                decode_state(state_after, system),
                actions
            )

            reward_sum += reward

            for i in range(len(agents)):
                if flags[i]:
                    agents[i].update(state, action_indices[i], reward, state_after)

            state = state_after

        print(f"Episode {ep + 1}/{episodes} finished. Reward: {reward_sum}")
        print(agents_group.agents[0].epsilon, agents_group.agents[1].epsilon, )
        whole_reward += reward_sum

    return QLearningAgentsGroup(agents), whole_reward / episodes


if __name__ == "__main__":

    rewards = []
    buffer_size = 25
    agt1 = QLearningAgent(ACTIONS, gamma=0.96, alpha=0.5, buffer_size=buffer_size)
    agt2 = QLearningAgent(ACTIONS, gamma=0.96, alpha=0.5, buffer_size=buffer_size)

    group = QLearningAgentsGroup([agt1, agt2])

    # group = QLearningAgentsGroup.load(
    #     r"C:\Users\Mateusz\projects\elevator-project\database\models\q_learning\third_validation_scenario_2_5.pkl")
    group.agents[0].epsilon_decay = 0.999998
    group.agents[1].epsilon_decay = 0.999998
    group.agents[0].epsilon = 0.6
    group.agents[1].epsilon = 0.6
    group.agents[0].gamma = 0.95
    group.agents[1].gamma = 0.95
    group.agents[0].alpha = 0.5
    group.agents[1].alpha = 0.5
    group.agents[0].epsilon_min = 0.35
    group.agents[1].epsilon_min = 0.35

    trained_group, reward = train_q_learning(
        episodes=20,
        steps=2500,
        agents_group=group
    )
    rewards.append(reward)

    n = 30

    for i in range(n):
        trained_group, reward = train_q_learning(
            episodes=20,
            steps=2500,
            agents_group=trained_group
        )
        rewards.append(reward)
        # if i % 500 == 0:
        #     trained_group.save(f"checkpoints/with_buffer{i / 1000}")
        #
        #     trained_group.save("experiment_no_buffer")

    trained_group.save("third_validation_scenario")

    # if i % 1000 == 0:
    #     trained_agent.save(f"checkpoints/with_buffer{i / 1000}")

    # trained_agent[0].save("experiment_no_buffer")
    # trained_agent.save_to_xlsx("q_matrix1.xlsx")

    x = np.linspace(0, n + 1, n + 1)
    y = np.array(rewards)

    a, b = np.polyfit(x, y, 1)  # y = a*x + b
    y_pred = a * x + b

    plt.scatter(x, y, label="Epizody")
    plt.plot(x, y_pred, color="red", label=f"Trend (a={a:.3f})")
    plt.xlabel("Iteracja treningu")
    plt.ylabel("Suma nagród na epizod (1000 kroków)")
    plt.title("Postęp uczenia")
    plt.suptitle(f"buffer size = {buffer_size}")
    plt.legend()
    plt.show()
