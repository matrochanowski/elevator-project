import pygame


class Renderer:
    BOTTOM_MARGIN = 30

    WIDTH = 800
    HEIGHT = 600
    FPS = 30


    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)

    def __init__(self, max_floor: int):
        self.max_floor = max_floor
        # Dynamically derived dimensions
        self.floor_height = (self.HEIGHT - self.BOTTOM_MARGIN) // (max_floor + 1)
        self.circle_radius = 15

    def draw(self, screen, system):
        """Main draw entrypoint."""
        # Floors
        for floor in range(self.max_floor + 1):
            self.draw_floor(screen, floor)

        # Passengers
        self.draw_passengers(screen, system.people_array)

        # Elevators
        self.draw_elevators(screen, system.elevators)

        # Requests
        self.draw_requests(screen, system)

    def draw_floor(self, screen, floor: int):
        """Draw floor line and floor number."""
        y = self.HEIGHT - self.BOTTOM_MARGIN - self.floor_height * (floor + 1)
        pygame.draw.line(screen, self.WHITE, (0, y), (self.WIDTH, y))

        font = pygame.font.Font(None, 24)
        text = font.render(str(floor), True, self.WHITE)
        screen.blit(text, (self.WIDTH - 40, self.HEIGHT - self.floor_height * (floor + 1) + 5))

    def draw_passengers(self, screen, people_array):
        """Draw passengers waiting on floors as circles with desired floor labels."""
        font = pygame.font.Font(None, 20)

        for floor in range(self.max_floor + 1):
            base_y = self.HEIGHT - self.BOTTOM_MARGIN - self.floor_height * floor - self.floor_height // 2

            for i, passenger in enumerate(people_array[floor]):
                if passenger is not None:
                    circle_x = 20 + i * (2 * self.circle_radius + 5)

                    pygame.draw.circle(screen, self.WHITE, (circle_x, base_y), self.circle_radius)

                    text = font.render(str(passenger.desired_floor), True, self.BLACK)
                    text_rect = text.get_rect(center=(circle_x, base_y))
                    screen.blit(text, text_rect)

    def draw_elevators(self, screen, elevators):
        """Draw all elevators dynamically spaced on the right side."""
        num_elevators = len(elevators)
        if num_elevators == 0:
            return

        available_width = self.WIDTH // 3
        spacing = 20
        elevator_width = max(20, (available_width - (num_elevators + 1) * spacing) // num_elevators)
        elevator_height = self.floor_height - 10

        font = pygame.font.Font(None, 24)
        arrow_font = pygame.font.Font(None, 28)

        for i, elevator in enumerate(elevators):
            x_position = self.WIDTH - available_width + spacing + i * (elevator_width + spacing) - 50
            y_position = self.HEIGHT - self.BOTTOM_MARGIN - self.floor_height * (elevator.current_floor + 1)

            color = self.GREEN if elevator.state == "STANDING" else self.RED

            pygame.draw.rect(screen, color, (x_position, y_position, elevator_width, elevator_height))

            # number of people inside
            text = font.render(str(len(elevator.people_inside_arr)), True, self.WHITE)
            text_rect = text.get_rect(
                center=(x_position + elevator_width // 2, y_position + elevator_height // 2)
            )
            screen.blit(text, text_rect)

            # --- direction arrow ---
            if elevator.state == "UP":
                arrow = "^"
            elif elevator.state == "DOWN":
                arrow = "v"
            else:
                arrow = ""

            if arrow:
                arrow_text = arrow_font.render(arrow, True, self.WHITE)
                if elevator.state == "DOWN":
                    arrow_rect = arrow_text.get_rect(
                        center=(x_position + elevator_width // 2, y_position + self.floor_height)
                    )
                else:
                    arrow_rect = arrow_text.get_rect(
                        center=(x_position + elevator_width // 2, y_position - 5)
                    )
                screen.blit(arrow_text, arrow_rect)

    def draw_requests(self, screen, system):
        """Draw requested floors + chosen floors by passengers inside elevators."""
        font = pygame.font.Font(None, 20)

        chosen = []
        for idx, elevator in enumerate(system.elevators, start=1):
            floors = [str(p.desired_floor) for p in elevator.people_inside_arr if p is not None]
            chosen.append(f"E{idx}: {', '.join(floors) if floors else '-'}")

        requested = [str(f) for f in sorted(system.requested_floors)]
        requested_text = f"Req: {', '.join(requested) if requested else '-'}"

        text = font.render(" | ".join(chosen + [requested_text]), True, self.WHITE)
        screen.blit(text, (10, self.HEIGHT - 25))
