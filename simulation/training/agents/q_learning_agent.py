import random
import numpy as np
import pickle
from collections import defaultdict

class QLearningAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.95, epsilon=0.1):
        self.q_table = defaultdict(lambda: np.zeros(len(actions)))
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def get_state(self, system):
        elevator = system.elevators[0]  # na początek tylko jedna winda
        floor = elevator.current_floor
        requests = tuple(1 if f in system.requested_floors else 0 for f in range(system.max_floor))
        return (floor, requests)

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randrange(len(self.actions))
        return int(np.argmax(self.q_table[state]))

    def update(self, state, action, reward, next_state):
        best_next = np.max(self.q_table[next_state])
        old_value = self.q_table[state][action]
        self.q_table[state][action] = old_value + self.alpha * (reward + self.gamma * best_next - old_value)

    # --- NEW: saving & loading ---
    def save(self, path: str):
        with open(path, "wb") as f:
            pickle.dump((dict(self.q_table), self.actions, self.alpha, self.gamma, self.epsilon), f)

    @classmethod
    def load(cls, path: str):
        with open(path, "rb") as f:
            q_table_dict, actions, alpha, gamma, epsilon = pickle.load(f)
        agent = cls(actions, alpha, gamma, epsilon)

        agent.q_table = defaultdict(lambda: np.zeros(len(actions)), q_table_dict)
        return agent
