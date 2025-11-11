class Person:
    def __init__(self, step, desired_floor=None, starting_floor=None):
        self.starting_floor = starting_floor
        self.desired_floor = desired_floor
        self.appearing_time = step

        self.journey_time = 0
        self.waiting_time = 0
        self.travel_time = 0

        self.state = "WAITING FOR ELEVATOR"  # POSSIBLE STATES ["WAITING FOR ELEVATOR", "IN ELEVATOR", "AT DESTINATION"]

    def __str__(self):
        return f"{self.journey_time, self.waiting_time, self.travel_time}"

    def increase_waiting_time(self, step=1):
        """
        Increase time of a person waiting
        :param step: How many steps
        :return:
        """
        match self.state:
            case "WAITING FOR ELEVATOR":
                self.journey_time += step
                self.waiting_time += step
            case "IN ELEVATOR":
                self.journey_time += step
                self.travel_time += step


    def enter_elevator(self):
        self.state = "IN ELEVATOR"

    def leave_elevator(self):
        self.state = "AT DESTINATION"
