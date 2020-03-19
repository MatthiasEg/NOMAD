from enum import Enum

from statemachine.radius_to_steering_angel_converter import RadiusToSteeringAngelConverter


class DrivingDirection(Enum):
    RIGHT = 1
    LEFT = -1
    STRAIGHT = 0


class SteeringCommandGeneratorResult:
    """
    Results of the SteeringCommandGenerator which are being sent to the uart node
    """

    def __init__(self, velocity_meters_per_second: float, curve_radius_centimeters: float) -> None:
<<<<<<< HEAD
        """

        :param velocity_meters_per_second:
        :param curve_radius_centimeters: 0 if driving straight, positive if driving right curve, negative if driving left curve
        """
        self._velocity_meters_per_second = velocity_meters_per_second
        self._steering_angel = 0 if curve_radius_centimeters == DrivingDirection.STRAIGHT.value else self._convert_radius_to_steering_angel(
            curve_radius_centimeters=curve_radius_centimeters)
=======
        self._velocity_meters_per_second = velocity_meters_per_second
        self._steering_angel = self._convert_radius_to_steering_angel(curve_radius_centimeters=curve_radius_centimeters)
>>>>>>> 67413c3a00c31a63c29d5512d43bba8feb89ca85

    @property
    def velocity_meters_per_second(self):
        return self._velocity_meters_per_second

    @property
    def steering_angel(self):
        return self._steering_angel

    @staticmethod
    def _convert_radius_to_steering_angel(curve_radius_centimeters: float) -> float:
        converter = RadiusToSteeringAngelConverter()
<<<<<<< HEAD
        return converter.convert(curve_radius_centimeters=curve_radius_centimeters)
=======
        return converter.convert(curve_radius_centimeters)
>>>>>>> 67413c3a00c31a63c29d5512d43bba8feb89ca85

    def __str__(self) -> str:
        return f"SteeringCommandGeneratorResult: [velocity={self._velocity_meters_per_second}, steering_angel={self._steering_angel}]"
