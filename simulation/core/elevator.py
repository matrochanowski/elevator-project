from simulation.core.elevator_system import ElevatorSystem


class Elevator:
    def __init__(self, max_people_inside, max_possible_floor, starting_floor=0, speed=5):
        self.current_floor = starting_floor
        self.people_inside_int = 0
        self.max_people_inside = max_people_inside
        self.max_possible_floor = max_possible_floor

        self.chosen_floors = []
        self.queue = None  # fully managed by operator
        self.state = "STANDING"
        self.people_inside_arr = []
        self.delay = 0
        self.speed = speed

    def enter(self, people_entering_arr):
        """
        Metoda obsługująca osoby wchodzące do windy
        :param people_entering_arr: lista z obiektami klasy Person
        :return:
        """
        for person in people_entering_arr:
            self.people_inside_arr.append(person)
        self.update_people_inside()

    def leave(self, people_leaving_arr):
        """
        Metoda obsługująca osoby wysiadające z windy
        :param people_leaving_arr: lista z obiektami klasy Person
        :return:
        """
        for person in people_leaving_arr:
            self.people_inside_arr.remove(person)
        self.update_people_inside()

    def update_people_inside(self):
        """
        Metoda aktualizująca osoby w środku windy
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
        Zmień obecny stan windy na jadącą w gorę
        :return:
        """
        self.state = "UP"

    def state_down(self):
        """
        Zmień obecny stan windy na jadącą w dół
        :return:
        """
        self.state = "DOWN"

    def state_none(self):
        """
        Zmień obecny stan windy na stojącą
        :return:
        """
        self.state = "STANDING"

    def add_floor_to_chosen_queue(self, new_floor):
        """
        Metoda dodająca piętro do listy z wybranymi piętrami (z zewnątrz)
        :param new_floor: indeks piętra
        :return:
        """
        self.chosen_floors.append(new_floor)

    def remove_floor_from_chosen(self, floor):
        """
        Metoda usuwająca piętro z listy z wybranymi piętrami (z zewnątrz)
        :param floor: indeks piętra
        :return:
        """
        if floor in self.chosen_floors:
            self.chosen_floors.remove(floor)

    def decide_if_stop(self, elevator_system: ElevatorSystem):
        """
        Metoda decydująca, czy winda powinna zatrzymać się na danym piętrze
        :param elevator_system: Obiekt klasy ElevatorSystem
        :return: True or False
        """
        if self.current_floor in elevator_system.requested_floors:
            return True
        if self.current_floor in self.chosen_floors:
            return True
        return None

    def increase_floor(self):
        """
        Metoda zwiększająca piętro windy o 1
        :return:
        """
        if self.current_floor + 1 > self.max_possible_floor:
            pass
        else:
            self.current_floor += 1

    def decrease_floor(self):
        """
        Metoda zmniejszająca piętro windy o 1
        :return:
        """
        if self.current_floor - 1 < 0:
            pass
        else:
            self.current_floor -= 1

    def how_much_space_left(self):
        """
        :return: Ile osób może się jeszcze zmieścić do windy
        """
        return self.max_people_inside - self.people_inside_int
