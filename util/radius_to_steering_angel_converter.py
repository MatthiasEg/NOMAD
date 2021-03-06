import logging

import numpy as np


class RadiusToSteeringAngelConverter:
    def __init__(self) -> None:
        self._logger = logging.getLogger("RadiusToSteeringAngelConverter")
        self._wheel_distance: float = 25.1  # centimeters
        self._distance_center_of_gravity_read_wheels: float = 11.957  # centimeters

    def convert(self, curve_radius_centimeters: float) -> float:
        if curve_radius_centimeters < 0:  # driving left curve
            return 180/np.pi * (-1) * np.arctan(
                self._wheel_distance / (np.sqrt((curve_radius_centimeters ** 2) - (self._distance_center_of_gravity_read_wheels ** 2))))
        elif curve_radius_centimeters > 0:  # driving right curve
            return 180/np.pi * np.arctan(self._wheel_distance / (np.sqrt((curve_radius_centimeters ** 2) - (self._distance_center_of_gravity_read_wheels ** 2))))
        else:
            self._logger.error("Curve radius was 0, which should not be possible here!")
