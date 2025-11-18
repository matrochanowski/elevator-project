from simulation import config
from simulation.core.elevator import Elevator
from simulation.core.elevator import ElevatorSystem
from simulation.engine.step_operator import operator
from simulation.training.agents.q_learning_agent import QLearningAgent
from simulation.training.scripts.utils import *
import time

import matplotlib.pyplot as plt
import numpy as np

cfg = config.load_config()

ACTIONS = ["UP", "DOWN", "STANDING"]


def train_q_learning(episodes=100, steps=200, agent=QLearningAgent(ACTIONS)):
    whole_reward = 0
    flag = False
    for ep in range(episodes):
        system = ElevatorSystem(cfg.floors, cfg.max_people_floor)
        system.elevators = [Elevator(max_people_inside=elevator.max_people,
                                     max_possible_floor=cfg.floors,
                                     speed=elevator.speed) for elevator in cfg.elevators]

        prev_served = 0
        state = get_state(system)
        reward_sum = 0

        for step in range(steps):
            if system.elevators[0].delay == 0:
                flag = True
            else:
                flag = False

            action_idx = agent.choose_action(state)
            actions = [ACTIONS[action_idx]]

            state_before = get_state(system)
            system = operator(actions, system, step=0)
            state_after = get_state(system)

            reward = reward_function(decode_state(state_before, system), decode_state(state_after, system), actions)
            reward_sum += reward

            if flag:
                # print("-!-" * 20)
                # print(f"STAN PRZED: {state_before}")
                # print(f"AKCJA: {actions}")
                # print(f"STAN PO: {state_after}")
                # print(f"NAGRODA: {reward}")
                # print("Czy stan się zmienił? ", state_before != state_after)
                # print("-!-" * 20)
                agent.update(state, action_idx, reward, state_after)

            state = state_after

        print(f"Episode {ep + 1}/{episodes} finished. Reward: {reward_sum}")
        whole_reward += reward_sum

    return agent, whole_reward / episodes


if __name__ == "__main__":
    rewards = []
    buffer_size = 0
    agt = QLearningAgent(ACTIONS, gamma=0.96, alpha=0.5, buffer_size=buffer_size)
    trained_agent, reward = train_q_learning(episodes=5, steps=1000, agent=agt)
    rewards.append(reward)

    n = 20

    for i in range(n):
        trained_agent, reward = train_q_learning(episodes=20, steps=1000, agent=trained_agent)
        rewards.append(reward)

        # if i % 1000 == 0:
        #     trained_agent.save(f"checkpoints/with_buffer{i / 1000}")

    trained_agent.save("experiment_no_buffer")
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
