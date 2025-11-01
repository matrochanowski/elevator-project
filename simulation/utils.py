from typing import Tuple


def extract_params_suffix(filename: str) -> Tuple[int, int]:
    """
    :param filename: whole filename (with .pkl extension).
    :return: number of elevators, number of floors
    """
    n_floors_str = ""
    elevators_done_flag = False
    n_elevators_str = ""
    floors_done_flag = False
    for i in range(len(filename) - 4, 0, -1):
        if i == 0:
            n_floors_str = filename[i - 1]
            continue
        if not floors_done_flag:
            if filename[i - 1] == "_":
                floors_done_flag = True
                continue
            n_floors_str = filename[i - 1] + n_floors_str
            continue
        if not elevators_done_flag:
            if filename[i - 1] == "_":
                elevators_done_flag = True
                continue
            n_elevators_str = filename[i - 1] + n_elevators_str

    try:
        n_elevators = int(n_elevators_str)
    except ValueError:
        return 0, 0
    try:
        n_floors = int(n_floors_str)
    except ValueError:
        return 0, 0
    return n_elevators, n_floors
