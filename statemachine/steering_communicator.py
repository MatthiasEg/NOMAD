from typing import Any

from communication.sender import Sender
from statemachine.steering_command_generator_result import SteeringCommandGeneratorResult, DrivingDirection


class SteeringCommunicator:
    """
    Communicates between SteeringCommandGenerator and Uart Connector
    """
    _sender: Sender
    _last_steering_command_sent: SteeringCommandGeneratorResult = SteeringCommandGeneratorResult(velocity_meters_per_second=0,
                                                                                                 curve_radius_centimeters=0,
                                                                                                 driving_direction=DrivingDirection.STRAIGHT)

    def send(self, velocity_meters_per_second: float,
             curve_radius_centimeters: float = None,
             driving_direction: DrivingDirection = None):
        """
        Sends SteeringCommandGeneratorResult to Uart Node.

        :param velocity_meters_per_second: velocity in meters per second NOMAD should achieve with this steering command
        :param curve_radius_centimeters: optional parameter - if not provided it will take the last sent radius.
        :param driving_direction: optional parameter - if not provided it will take the last sent driving direction.
        :return:
        """
        if curve_radius_centimeters is None and driving_direction is None:
            command = SteeringCommandGeneratorResult(velocity_meters_per_second=velocity_meters_per_second,
                                                     curve_radius_centimeters=self._last_steering_command_sent.curve_radius_centimeters,
                                                     driving_direction=self._last_steering_command_sent.driving_direction)
        elif curve_radius_centimeters is not None and driving_direction is not None:
            command = SteeringCommandGeneratorResult(velocity_meters_per_second=velocity_meters_per_second,
                                                     curve_radius_centimeters=curve_radius_centimeters,
                                                     driving_direction=driving_direction)
        elif curve_radius_centimeters is None:
            command = SteeringCommandGeneratorResult(velocity_meters_per_second=velocity_meters_per_second,
                                                     curve_radius_centimeters=self._last_steering_command_sent.curve_radius_centimeters,
                                                     driving_direction=driving_direction)
        else:
            command = SteeringCommandGeneratorResult(velocity_meters_per_second=velocity_meters_per_second,
                                                     curve_radius_centimeters=curve_radius_centimeters,
                                                     driving_direction=self._last_steering_command_sent.curve_radius_centimeters)
        self._last_steering_command_sent = command
        self._sender.send(command)

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, new_sender: Sender):
        self._sender = new_sender

    def last_sent_velocity(self) -> float:
        return self._last_steering_command_sent.velocity_meters_per_second
