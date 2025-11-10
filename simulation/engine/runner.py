from simulation import config

from simulation.core.elevator_system import ElevatorSystem
from simulation.core.elevator import Elevator

from simulation.engine.step_operator import operator
from simulation.engine.logger import SimulationLogger

from simulation.visualisation.renderer import Renderer

from simulation.training.scripts.utils import *

# ALGORITHM = nearest_car_policy
# agent = AgentController("q_agent_simple_reward_1_3.pkl")
# ALGORITHM = agent.use_agent


cfg = config.load_config()

ALGORITHM = cfg.algorithm.get_controller(model=cfg.model)


def run_simulation(steps: int, system: ElevatorSystem, policy, visualisation, renderer):
    screen = None
    clock = None
    pygame = None

    if visualisation:
        import pygame
        pygame.init()
        screen = pygame.display.set_mode((renderer.WIDTH, renderer.HEIGHT))
        pygame.display.set_caption("Elevator Simulation")
        clock = pygame.time.Clock()

    running = True
    step_count = 0
    logger = SimulationLogger()

    while running and step_count < steps:
        # --- Event Handling ---
        if visualisation:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        # --- Simulation Step ---
        previous_state = get_state(system)

        actions = policy(system)
        _, system, _ = operator(actions, system, step_count)
        logger.log_step(step_count, system)

        current_state = get_state(system)

        reward = reward_function(decode_state(previous_state, system), decode_state(current_state, system), actions)

        # print(reward)

        # --- Drawing only in visualisation mode ---
        if visualisation:
            screen.fill(renderer.BLACK)
            renderer.draw(screen, system)
            pygame.display.flip()
            clock.tick(15)

        step_count += 1

    if visualisation:
        pygame.quit()

    logger.finalize()

    return system


building = ElevatorSystem(cfg.floors, 25, cfg.max_people_floor)
building.elevators = [Elevator(max_people_inside=elevator.max_people,
                               max_possible_floor=cfg.floors,
                               speed=elevator.speed) for elevator in cfg.elevators]
renderer_obj = Renderer(cfg.floors)
print(run_simulation(cfg.steps, building, ALGORITHM, cfg.visualisation, renderer_obj))
