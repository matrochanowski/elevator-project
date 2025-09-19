from simulation import config

from simulation.controller.classical.nearest_car_policy import nearest_car_policy

from simulation.core.elevator_system import ElevatorSystem
from simulation.core.elevator import Elevator

from simulation.engine.step_operator import operator

from simulation.visualisation.renderer import Renderer

ALGORITHM = nearest_car_policy

cfg = config.load_config()


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

    while running and step_count < steps:
        # --- Event Handling (tylko w trybie viz) ---
        if visualisation:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        # --- Simulation Step ---
        actions = policy(system)
        _, system, _ = operator(actions, system)

        # --- Drawing (tylko w trybie viz) ---
        if visualisation:
            screen.fill(renderer.BLACK)
            renderer.draw(screen, system)
            pygame.display.flip()
            clock.tick(15)

        step_count += 1

    if visualisation:
        pygame.quit()

    return system


building = ElevatorSystem(cfg.floors, 25, cfg.max_people_floor)
building.elevators = [Elevator(max_people_inside=elevator.max_people,
                               max_possible_floor=cfg.floors,
                               speed=elevator.speed) for elevator in cfg.elevators]
renderer_obj = Renderer(cfg.floors)
print(run_simulation(cfg.steps, building, ALGORITHM, cfg.visualisation, renderer_obj))
