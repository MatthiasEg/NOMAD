from enum import Enum


class Situation(Enum):
    no_object_in_front = 0
    pylon_far_away = 1
    only_pylon_in_front = 2
    square_timber_in_front_of_pylon = 3
    only_square_timber_in_front = 4
    square_timber_behind_pylon = 5
    ignore = 6
