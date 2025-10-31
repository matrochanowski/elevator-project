from simulation import config
from simulation.core.elevator import Elevator
from simulation.core.elevator import ElevatorSystem
from simulation.engine.step_operator import operator
from simulation.training.agents.q_learning_agent import QLearningAgent
from simulation.training.scripts.utils import *

import matplotlib.pyplot as plt
import numpy as np

cfg = config.load_config()

ACTIONS = ["UP", "DOWN", "STANDING"]


def train_q_learning(episodes=100, steps=200, agent=QLearningAgent(ACTIONS)):
    whole_reward = 0
    for ep in range(episodes):
        system = ElevatorSystem(cfg.floors, 50, cfg.max_people_floor)
        system.elevators = [Elevator(max_people_inside=elevator.max_people,
                                     max_possible_floor=cfg.floors,
                                     speed=elevator.speed) for elevator in cfg.elevators]

        prev_served = 0
        state = get_state(system)
        reward_sum = 0

        for step in range(steps):
            action_idx = agent.choose_action(state)
            actions = [ACTIONS[action_idx]]

            state_before = get_state(system)
            _, system, _ = operator(actions, system)
            state_after = get_state(system)

            reward = reward_function(decode_state(state_before, system), decode_state(state_after, system), actions)
            reward_sum += reward

            if system.elevators[0].delay >= 0:
                agent.update(state, action_idx, reward, state_after)

            state = state_after

        print(f"Episode {ep + 1}/{episodes} finished. Reward: {reward_sum}")
        whole_reward += reward_sum

    return agent, whole_reward / episodes


if __name__ == "__main__":
    rewards = []
    trained_agent, reward = train_q_learning(episodes=5, steps=1000)
    rewards.append(reward)

    n = 300

    for i in range(n):
        trained_agent, reward = train_q_learning(episodes=5, steps=1000, agent=trained_agent)
        rewards.append(reward)

    trained_agent.save("q_agent_simple_reward.pkl")
    trained_agent.save_to_xlsx("q_matrix1.xlsx")

    x = np.linspace(0, n + 1, n + 1)
    y = np.array(rewards)

    a, b = np.polyfit(x, y, 1)  # y = a*x + b
    y_pred = a * x + b

    plt.scatter(x, y, label="Epizody")
    plt.plot(x, y_pred, color="red", label=f"Trend (a={a:.3f})")
    plt.xlabel("Iteracja treningu")
    plt.ylabel("Suma nagród na epizod (1000 kroków)")
    plt.title("Postęp uczenia: funkcja nagrody nr 2")
    plt.legend()
    plt.show()
