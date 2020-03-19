import logging
from typing import List

from transitions import State

from communication.sender import Sender
from object_detection.object_detector.object_detector_result import ObjectDetectorResult
from statemachine.danger_zone import DangerZone
from statemachine.states_nomad import States
from statemachine.steering_command_generator_result import SteeringCommandGeneratorResult
from statemachine.transitions_nomad import Transitions


class Nomad:
    """
    Might be used as model for the state machine.
    """

    def __init__(self):
        self._sender = None
        self._logger = logging.getLogger("NomadModel")
        self._state = None
        self._data = None
        self._velocity = 0

    def slow_down(self):
        """
        State: ObstacleDetected
        After detecting an Obstacle Nomad should slow down to a defined speed. Only slow down if
        the max velocity is not already reached.
        :return:
        """

        pass

    def align_horizontal_to_obstacle(self):
        pass

    def drive_orbit(self):
        """
        State: OrbitEntered
        :return:
        """
        # drive orbit with radius of 1 meter or 0.5 meter depending of measured distance
        # scan for pylon while driving, if one is detected keep driving until it is centered
        # then drive towards pylon
        self.trigger(Transitions.OrbitEntered_to_PylonTargeted.name)
        # if obstacle is detected in front of nomad, goto state obstacle detected
        self.trigger(Transitions.OrbitEntered_to_ObstacleDetected.name)
        # if in next frames pylon to the right side is detected drive fi
        self.drive_fictitious_pylon_orbit()
        self.trigger(Transitions.OrbitEntered_to_DestinationPylonUnknown)
        pass

    def drive_towards_targeted_pylon(self):
        """
        State: OrbitTargeted, TransitEndangered
        :return:
        """
        # if in state
        self._logger.debug("DRIVING....")
        if self.state == States.OrbitTargeted.name:
            # drive towards pylon and measure distance
            # watch out for pylons on right side of targeted pylon

            pass
        elif self.state == States.TransitEndangered.name:
            # drive towards pylon
            # measure distance to horizontal axis of pylon in danger zone
            # if obstacle in front of nomad detected and distance < 0.5m
            self.trigger(Transitions.TransitEndangered_to_ObstacleDetected.name)

            # if distance to horizontal axis of pylon in danger zone <=1m do drive_fictitious_pylon_orbit
            if False:
                self.drive_fictitious_pylon_orbit()
                self.trigger(Transitions.TransitEndangered_to_DestinationPylonUnknown.name)
            pass

    def is_pylon_in_danger_zone(self):
        """
        State: PylonTargeted
        :return:
        """
        # if in danger zone switch to
        self._logger.debug("Is Pylon in danger zone?")
        danger_zone = DangerZone()
        if danger_zone.is_relevant():
            self.trigger(Transitions.PylonTargeted_to_TransitEndangered.name)
        else:
            self.trigger(Transitions.PylonTargeted_to_OrbitTargeted.name)

    def measure_distance_to_pylon(self):
        """
        State:
        :return:
        """
        # measure distance to pylon
        #
        pass

    def scan_for_pylons(self):
        """
        State: DestinationPylonUnknown
        :return:
        """
        # process data and initiate transitions to next state if pylon is detected and in center.
        # if nothing is found, keep scanning while driving
        # if pylon is still to much on left side, keep driving on circle until pylon perfectly in front

        # if pylon is centered
        self.trigger(Transitions.DestinationPylonUnknown_to_PylonTargeted.name)

    def drive_fictitious_pylon_orbit(self):
        """
        State: on_exit Start
        :return:
        """
        self._logger.debug("Driving fictitious pylon orbit")
        self._sender.send(py_object=SteeringCommandGeneratorResult(velocity_meters_per_second=2, curve_radius=30))
        # do driving stuff

    def start_state_machine(self):
        """
        State: Start
        :return:
        """
        self._logger.debug("Starting State Machine...")
        self.drive_fictitious_pylon_orbit()
        self.trigger(Transitions.Start_to_DestinationPylonUnknown.name)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, current_result: ObjectDetectorResult):
        self._data = current_result

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, new_sender: Sender):
        self._sender = new_sender

    @property
    def state(self):
        return self._state
