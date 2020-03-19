import numpy as np


class RadiusToSteeringAngelConverter:
    def __init__(self) -> None:
        self._wheel_distance = 250  # millimetre
        self._distance_center_of_gravity_read_wheels = 150  # millimetre

    def convert(self, curve_radius_centimeters: float) -> float:
        return np.arctan(
            self._wheel_distance / np.sqrt((curve_radius_centimeters ** 2) - (self._distance_center_of_gravity_read_wheels ** 2)))
