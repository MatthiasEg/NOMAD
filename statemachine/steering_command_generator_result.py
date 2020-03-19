from statemachine.radius_to_steering_angel_converter import RadiusToSteeringAngelConverter


class SteeringCommandGeneratorResult:
    """
    Results of the SteeringCommandGenerator which are being sent to the uart node
    """

    def __init__(self, velocity_meters_per_second: float, curve_radius_centimeters: float) -> None:
        self._velocity_meters_per_second = velocity_meters_per_second
        self._steering_angel = self._convert_radius_to_steering_angel(curve_radius_centimeters=curve_radius_centimeters)

    @property
    def velocity_meters_per_second(self):
        return self._velocity_meters_per_second

    @property
    def steering_angel(self):
        return self._steering_angel

    @staticmethod
    def _convert_radius_to_steering_angel(curve_radius_centimeters: float) -> float:
        converter = RadiusToSteeringAngelConverter()
        return converter.convert(curve_radius_centimeters)

    def __str__(self) -> str:
        return f"SteeringCommandGeneratorResult: [velocity={self._velocity_meters_per_second}, steering_angel={self._steering_angel}]"
