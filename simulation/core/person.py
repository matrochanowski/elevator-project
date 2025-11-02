import random


class Person:
    def __init__(self, max_floor, desired_floor=None, starting_floor=None):
        if starting_floor is None:
            choice = random.randint(0, 1)
            if choice == 0:
                self.starting_floor = 0
            else:
                self.starting_floor = random.randint(1, max_floor)
        else:
            self.starting_floor = starting_floor

        self.current_floor = starting_floor
        self.wait_time = 0

        if desired_floor is None:
            if self.starting_floor == 0:
                self.desired_floor = random.randint(1, max_floor)
            else:
                self.desired_floor = 0
        else:
            self.desired_floor = desired_floor

    def __str__(self):
        return f"{self.wait_time}"

    def increase_waiting_time(self, step=1):
        """
        Increase time of a person waiting
        :param step: How many steps
        :return:
        """
        self.wait_time += step
