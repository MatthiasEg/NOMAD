import logging

import numpy as np


class RadiusToSteeringAngelConverter:
    def __init__(self) -> None:
        self._logger = logging.getLogger("RadiusToSteeringAngelConverter")
        self._wheel_distance = 250  # millimetre
        self._distance_center_of_gravity_read_wheels = 150  # millimetre

    def convert(self, curve_radius_centimeters: float) -> float:
<<<<<<< HEAD
        if curve_radius_centimeters < 0:  # driving left curve
            return (-1) * np.arctan(self._wheel_distance / np.sqrt(
                (curve_radius_centimeters ** 2) - (self._distance_center_of_gravity_read_wheels ** 2)))
        elif curve_radius_centimeters > 0:  # driving right curve
            return np.arctan(self._wheel_distance / np.sqrt(
                (curve_radius_centimeters ** 2) - (self._distance_center_of_gravity_read_wheels ** 2)))
        else:
            self._logger.error("Curve radius was 0, which should not be possible here!")
=======
        return np.arctan(
            self._wheel_distance / np.sqrt((curve_radius_centimeters ** 2) - (self._distance_center_of_gravity_read_wheels ** 2)))
>>>>>>> 67413c3a00c31a63c29d5512d43bba8feb89ca85
