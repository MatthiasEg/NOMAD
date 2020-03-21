from enum import Enum

from util.radius_to_steering_angel_converter import RadiusToSteeringAngelConverter


class DrivingDirection(Enum):
    RIGHT = 1
    LEFT = -1
    STRAIGHT = 0


class SteeringCommandGeneratorResult:
    """
    Results of the SteeringCommandGenerator which are being sent to the uart node
    """

    def __init__(self, velocity_meters_per_second: float, curve_radius_centimeters: float, driving_direction: DrivingDirection) -> None:
        """
        :param velocity_meters_per_second:
        :param curve_radius_centimeters: determines the radius NOMAD needs to drive
        :param driving_direction: RIGHT for a right curve, LEFT for a left curve and STRAIGHT to drive straight ahead
        """
        if curve_radius_centimeters < 0:
            raise ValueError(f'curve_radius_centimeters must be positive value but is: {curve_radius_centimeters}')

        self._driving_direction: DrivingDirection = driving_direction
        self._velocity_meters_per_second = velocity_meters_per_second
        self._curve_radius_centimeters = curve_radius_centimeters

        if driving_direction == DrivingDirection.LEFT:
            curve_radius_centimeters = curve_radius_centimeters * (-1)
        self._steering_angel = 0 if curve_radius_centimeters == DrivingDirection.STRAIGHT.value else self._convert_radius_to_steering_angel(
            curve_radius_centimeters=curve_radius_centimeters)

    @property
    def velocity_meters_per_second(self):
        return self._velocity_meters_per_second

    @property
    def steering_angel(self):
        return self._steering_angel

    @property
    def driving_direction(self):
        return self._driving_direction

    @property
    def curve_radius_centimeters(self):
        return self._curve_radius_centimeters

    @staticmethod
    def _convert_radius_to_steering_angel(curve_radius_centimeters: float) -> float:
        converter = RadiusToSteeringAngelConverter()
        return converter.convert(curve_radius_centimeters=curve_radius_centimeters)

    def __str__(self) -> str:
        return f"SteeringCommandGeneratorResult: [velocity={self._velocity_meters_per_second}, steering_angel={self._steering_angel}]"
