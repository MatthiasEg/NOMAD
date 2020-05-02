from typing import Any

from transitions import State

from communication.sender import Sender
from statemachine.steering_command_generator_result import SteeringCommandGeneratorResult, DrivingDirection


class SteeringCommunicator:
    """
    Communicates between SteeringCommandGenerator and Uart Connector
    """
    _sender: Sender
    _last_steering_command_sent: SteeringCommandGeneratorResult = None

    def send(self, velocity_meters_per_second: float,
             curve_radius_centimeters: float = None,
             driving_direction: DrivingDirection = None,
             state_nomad: State = None):
        """
        Sends SteeringCommandGeneratorResult to Uart Node.

        :param state_nomad: Current State of the state machine
        :param velocity_meters_per_second: velocity in meters per second NOMAD should achieve with this steering command
        :param curve_radius_centimeters: optional parameter - if not provided it will take the last sent radius.
        :param driving_direction: optional parameter - if not provided it will take the last sent driving direction.
        :return:
        """
        if curve_radius_centimeters is None and driving_direction is None:
            command = SteeringCommandGeneratorResult(velocity_meters_per_second=velocity_meters_per_second,
                                                     curve_radius_centimeters=self._last_steering_command_sent.curve_radius_centimeters,
                                                     driving_direction=self._last_steering_command_sent.driving_direction,
                                                     state_nomad=state_nomad)
        elif curve_radius_centimeters is not None and driving_direction is not None:
            command = SteeringCommandGeneratorResult(velocity_meters_per_second=velocity_meters_per_second,
                                                     curve_radius_centimeters=curve_radius_centimeters,
                                                     driving_direction=driving_direction,
                                                     state_nomad=state_nomad)
        elif curve_radius_centimeters is None:
            command = SteeringCommandGeneratorResult(velocity_meters_per_second=velocity_meters_per_second,
                                                     curve_radius_centimeters=self._last_steering_command_sent.curve_radius_centimeters,
                                                     driving_direction=driving_direction,
                                                     state_nomad=state_nomad)
        else:
            command = SteeringCommandGeneratorResult(velocity_meters_per_second=velocity_meters_per_second,
                                                     curve_radius_centimeters=curve_radius_centimeters,
                                                     driving_direction=self._last_steering_command_sent.curve_radius_centimeters,
                                                     state_nomad=state_nomad)
        self._last_steering_command_sent = command
        self._sender.send(command)

    def resend_last_steering_command(self, new_state: State):
        self._sender.send(SteeringCommandGeneratorResult(velocity_meters_per_second=self._last_steering_command_sent.velocity_meters_per_second,
                                                         curve_radius_centimeters=self._last_steering_command_sent.curve_radius_centimeters,
                                                         driving_direction=self._last_steering_command_sent.driving_direction,
                                                         state_nomad=new_state))

    def last_sent_velocity(self) -> float:
        return self._last_steering_command_sent.velocity_meters_per_second

    @property
    def sender(self) -> Sender:
        return self._sender

    @sender.setter
    def sender(self, new_sender: Sender):
        self._sender = new_sender

    def last_sent_velocity(self) -> float:
        return self._last_steering_command_sent.velocity_meters_per_second
