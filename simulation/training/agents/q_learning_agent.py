import random
import numpy as np
import pickle
from collections import defaultdict, deque
from openpyxl import Workbook
from pathlib import Path
from typing import List
import os
from simulation import config

TRAINING_ROOT = Path(__file__).resolve().parents[1]
MODELS_DATABASE = Path(__file__).resolve().parents[3] / "database" / "models" / "q_learning"
cfg = config.load_config()


class QLearningAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.95, epsilon=0.5, epsilon_decay=0, buffer_size=0):
        self.q_table = defaultdict(lambda: np.zeros(len(actions)))
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.buffer_size = buffer_size
        self.buffer = deque(maxlen=buffer_size)
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = 0.05

    def choose_action(self, state):
        self.decay_epsilon()
        if random.random() < self.epsilon:
            return random.randrange(len(self.actions))
        return int(np.argmax(self.q_table[state]))

    def update(self, state, action, reward, next_state):
        match self.buffer_size:
            case 0:
                return self.update_no_buffer(state, action, reward, next_state)
            case _:
                return self.update_with_buffer(state, action, reward, next_state)

    def update_with_buffer(self, state, action, reward, next_state):
        self.buffer.append((state, action, reward, next_state))

        if len(self.buffer) >= self.buffer_size:
            while len(self.buffer) > 0:
                state, action, reward, next_state = self.buffer.pop()
                best_next = np.max(self.q_table[next_state])
                old_value = self.q_table[state][action]
                self.q_table[state][action] = old_value + self.alpha * (reward + self.gamma * best_next - old_value)

    def update_no_buffer(self, state, action, reward, next_state):
        best_next = np.max(self.q_table[next_state])
        old_value = self.q_table[state][action]
        self.q_table[state][action] = old_value + self.alpha * (reward + self.gamma * best_next - old_value)

    def decay_epsilon(self):
        if self.epsilon < self.epsilon_min:  # in case we want 0 epsilon for control
            return
        decay_rate = self.epsilon_decay
        self.epsilon = max(self.epsilon_min, self.epsilon * decay_rate)

    def save(self, filename: str):
        """
        Saves the current parameters into a pkl file in training/models directory.
        your_name_{n_elevators}_{n_floors}.pkl
        :param filename: Name of the model. Don't add extension here.
        :return:
        """
        suffix = "_" + str(len(cfg.elevators)) + "_" + str(cfg.floors)
        whole_path = os.path.join(TRAINING_ROOT, "models", filename + suffix + ".pkl")
        group = QLearningAgentsGroup([self])
        group.save(filename)

    def save_to_xlsx(self, path: str):
        wb = Workbook()
        ws = wb.active
        ws.title = "Q-Table"

        ws.append(["State"] + [f"Action {a}" for a in self.actions])

        for state, q_values in self.q_table.items():
            ws.append([str(state)] + list(map(float, q_values)))

        wb.save(path)
        print(f"Q-table saved to {path}")

    @classmethod
    def load(cls, path: str, alpha=None, gamma=None, epsilon=None):
        with open(path, "rb") as f:
            q_table_dict, actions, alpha_load, gamma_load, epsilon_load = pickle.load(f)
        if alpha is None:
            alpha = alpha_load
        if gamma is None:
            gamma = gamma_load
        if epsilon is None:
            epsilon = epsilon_load
        agent = cls(actions, alpha, gamma, epsilon)

        agent.q_table = defaultdict(lambda: np.zeros(len(actions)), q_table_dict)
        return agent


class QLearningAgentsGroup:
    def __init__(self, agents: List[QLearningAgent]):
        self.agents = agents

    def save(self, filename: str) -> str:
        suffix = "_" + str(len(cfg.elevators)) + "_" + str(cfg.floors)
        whole_path = os.path.join(MODELS_DATABASE, filename + suffix + ".pkl")

        data = []
        for agent in self.agents:
            data.append({
                "q_table": dict(agent.q_table),
                "actions": agent.actions,
                "alpha": agent.alpha,
                "gamma": agent.gamma,
                "epsilon": agent.epsilon
            })

        with open(whole_path, "wb") as f:
            pickle.dump(data, f)

        return whole_path

    @classmethod
    def load(cls, path: str):
        with open(path, "rb") as f:
            loaded = pickle.load(f)

        agents = []
        for entry in loaded:
            agent = QLearningAgent(
                actions=entry["actions"],
                alpha=entry["alpha"],
                gamma=entry["gamma"],
                epsilon=entry["epsilon"]
            )
            agent.q_table = defaultdict(lambda: np.zeros(len(entry["actions"])), entry["q_table"])
            agents.append(agent)

        return cls(agents)
