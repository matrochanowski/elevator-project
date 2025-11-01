import random
import numpy as np
import pickle
from collections import defaultdict
from openpyxl import Workbook
from pathlib import Path
import os
from simulation import config

TRAINING_ROOT = Path(__file__).resolve().parents[1]
cfg = config.load_config()


class QLearningAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.95, epsilon=0.5):
        self.q_table = defaultdict(lambda: np.zeros(len(actions)))
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randrange(len(self.actions))
        return int(np.argmax(self.q_table[state]))

    def update(self, state, action, reward, next_state):
        best_next = np.max(self.q_table[next_state])
        old_value = self.q_table[state][action]
        self.q_table[state][action] = old_value + self.alpha * (reward + self.gamma * best_next - old_value)

    def save(self, filename: str):
        """
        Saves the current parameters into a pkl file in training/models directory.
        your_name_{n_elevators}_{n_floors}.pkl
        :param filename: Name of the model. Don't add extension here.
        :return:
        """
        suffix = "_" + str(len(cfg.elevators)) + "_" + str(cfg.floors)
        whole_path = os.path.join(TRAINING_ROOT, "models", filename + suffix + ".pkl")
        with open(whole_path, "wb") as f:
            pickle.dump((dict(self.q_table), self.actions, self.alpha, self.gamma, self.epsilon), f)

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
    def load(cls, path: str):
        with open(path, "rb") as f:
            q_table_dict, actions, alpha, gamma, epsilon = pickle.load(f)
        agent = cls(actions, 0, 0.95, 0)

        agent.q_table = defaultdict(lambda: np.zeros(len(actions)), q_table_dict)
        return agent
