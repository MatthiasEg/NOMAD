class SteeringCommandGeneratorResult:
    """
    Results of the SteeringCommandGenerator which are being sent to the uart node
    """

    def __init__(self, velocity: float, steering_angel: float) -> None:
        self._velocity = velocity
        self._steering_angel = steering_angel

    def __str__(self) -> str:
        return f"SteeringCommandGeneratorResult: [velocity={self._velocity}, steering_angel={self._steering_angel}]"
