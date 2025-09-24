from simulation import config
from simulation.core.elevator_system import ElevatorSystem
from simulation.core.elevator import Elevator
from simulation.engine.step_operator import operator
from simulation.training.agents.q_learning_agent import QLearningAgent

cfg = config.load_config()

ACTIONS = ["UP", "DOWN", "STANDING"]


def reward_function(system, prev_served, served_now):
    """
    Nagroda = liczba obsłużonych pasażerów od ostatniego kroku
              - kara za liczbę oczekujących.
    """
    reward = (served_now - prev_served) * 10
    reward -= len(system.requested_floors)
    return reward


def train_q_learning(episodes=100, steps=200, agent=QLearningAgent(ACTIONS)):
    for ep in range(episodes):
        system = ElevatorSystem(cfg.floors, 25, cfg.max_people_floor)
        system.elevators = [Elevator(max_people_inside=elevator.max_people,
                                     max_possible_floor=cfg.floors,
                                     speed=elevator.speed) for elevator in cfg.elevators]

        prev_served = 0
        state = agent.get_state(system)
        reward_sum = 0

        for step in range(steps):
            action_idx = agent.choose_action(state)
            actions = [ACTIONS[action_idx]]  # tylko jedna winda na start

            served_before = len(system.passengers_at_dest)
            _, system, _ = operator(actions, system)
            served_after = len(system.passengers_at_dest)

            reward = reward_function(system, served_before, served_after)
            reward_sum += reward
            next_state = agent.get_state(system)

            agent.update(state, action_idx, reward, next_state)
            state = next_state

        print(f"Episode {ep + 1}/{episodes} finished. Reward: {reward_sum}")

    print(agent.q_table)

    return agent


if __name__ == "__main__":
    trained_agent = train_q_learning(episodes=500)
    # trained_agent = train_q_learning(episodes=1000, agent=trained_agent)
    # trained_agent = train_q_learning(episodes=1000, agent=trained_agent)
    # trained_agent = train_q_learning(episodes=1000, agent=trained_agent)
    # trained_agent = train_q_learning(episodes=1000, agent=trained_agent)
    # trained_agent = train_q_learning(episodes=1000, agent=trained_agent)

    trained_agent.save("q_agent.pkl")
