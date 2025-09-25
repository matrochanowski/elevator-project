from simulation.core.elevator_system import ElevatorSystem


class Elevator:
    def __init__(self,
                 max_people_inside,
                 max_possible_floor,
                 starting_floor=0,
                 speed=5,
                 time_at_floor=10,
                 acceleration_factor=0.05,
                 max_speed=5
                 ):
        self.current_floor = starting_floor
        self.people_inside_int = 0
        self.max_people_inside = max_people_inside
        self.max_possible_floor = max_possible_floor

        self.chosen_floors = []

        self.state = "STANDING"
        self.people_inside_arr = []
        self.delay = 0

        self.speed = speed  # this value says how much will
        # the elevator's delay increase after travelling up or down one floor

        self.time_at_floor = time_at_floor  # this value says how much will
        # the elevator's delay increase after stopping on a floor to serve passengers

        self.acc_factor = acceleration_factor
        self.max_speed = max_speed
        self.current_acc = 0

    def enter(self, people_entering_arr):
        """
        :param people_entering_arr: list of Person objects
        :return:
        """
        for person in people_entering_arr:
            self.people_inside_arr.append(person)
        self.update_people_inside()

    def leave(self, people_leaving_arr):
        """
        :param people_leaving_arr: list of Person objects
        :return:
        """
        for person in people_leaving_arr:
            self.people_inside_arr.remove(person)
        self.update_people_inside()

    def update_people_inside(self):
        """
        Updates the people inside the elevator
        :return:
        """
        self.people_inside_int = len(self.people_inside_arr)
        arr = []
        for person in self.people_inside_arr:
            arr.append(person.desired_floor)
            if person.desired_floor not in self.chosen_floors:
                self.add_floor_to_chosen_queue(person.desired_floor)
        for chosen_floor in self.chosen_floors:
            if chosen_floor not in arr:
                self.remove_floor_from_chosen(chosen_floor)

    def state_up(self):
        """
        Change the current elevator state to moving up
        :return:
        """
        self.state = "UP"

    def state_down(self):
        """
        Change the current elevator state to moving down
        :return:
        """
        self.state = "DOWN"

    def state_none(self):
        """
        Change the current elevator state to standing
        :return:
        """
        self.state = "STANDING"

    def add_floor_to_chosen_queue(self, new_floor):
        """
        Method for adding a floor to the chosen floors list (from outside)
        :param new_floor: floor index
        :return:
        """
        self.chosen_floors.append(new_floor)

    def remove_floor_from_chosen(self, floor):
        """
        Method for removing a floor from the chosen floors list (from outside)
        :param floor: floor index
        :return:
        """
        if floor in self.chosen_floors:
            self.chosen_floors.remove(floor)

    def decide_if_stop(self, elevator_system: ElevatorSystem):
        """
        Method deciding if the elevator should stop at the current floor
        :param elevator_system: ElevatorSystem object
        :return: True or False
        """
        if self.current_floor in elevator_system.requested_floors:
            return True
        if self.current_floor in self.chosen_floors:
            return True
        return None

    def increase_floor(self):
        """
        Method for increasing the elevator floor by 1
        :return:
        """
        if self.current_floor + 1 > self.max_possible_floor:
            pass
        else:
            self.current_floor += 1
        self.increase_delay_for_movement()

    def decrease_floor(self):
        """
        Method for decreasing the elevator floor by 1
        :return:
        """
        if self.current_floor - 1 < 0:
            pass
        else:
            self.current_floor -= 1
        self.increase_delay_for_movement()

    def how_much_space_left(self):
        """
        :return: How many people can still fit in the elevator
        """
        return self.max_people_inside - self.people_inside_int

    def increase_delay_for_movement(self):
        d = (self.speed - self.current_acc) / (1 + self.acc_factor)
        if d + self.delay < self.max_speed:
            self.delay += self.max_speed
            return
        self.current_acc = self.speed - d
        self.delay += round(d)
