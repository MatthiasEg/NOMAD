from typing import List

from shapely.geometry import Point

from communication.node import Node
from transitions import Machine, State
import logging

from communication.receiver import Receiver
from communication.sender import Sender
from object_detection.bounding_box import BoundingBox
from object_detection.object_detector.object_detector_result import ObjectDetectorResult, DetectedObject, \
    DetectedObjectType, Distance
from statemachine.danger_zone import DangerZone
from statemachine.states_nomad import States, StatesNomad
from statemachine.steering_command_generator_result import SteeringCommandGeneratorResult
from statemachine.transitions_nomad import TransitionsNomad, Transitions


class SteeringCommandGenerator(Node):
    _node_config_name = "STEERING_COMMAND_GENERATOR"
    _logger = logging.getLogger("SteeringCommandGenerator")

    def __init__(self):
        super().__init__(self._node_config_name)

        self._current_state = None
        self._states = StatesNomad().states

        self._state_machine = Machine(
            model=self,
            states=self._states,
            transitions=TransitionsNomad().transitions,
            initial=States.Start,
            auto_transitions=False,
            model_attribute='_current_state',
            queued=True
        )
        self._current_steering_result = SteeringCommandGeneratorResult()

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
        if self._state_machine.get_model_state(self) == States.OrbitTargeted.name:
            # drive towards pylon and measure distance
            # watch out for pylons on right side of targeted pylon

            pass
        elif self._state_machine.get_model_state(self) == States.TransitEndangered.name:
            # drive towards pylon
            # measure distance to horizontal axis of pylon in danger zone
            # if obstacle in front of nomad detected and distance < 0.5m
            self.trigger(Transitions.TransitEndangered_to_ObstacleDetected)

            # if distance to horizontal axis of pylon in danger zone <=1m do drive_fictitious_pylon_orbit
            if False:
                self.drive_fictitious_pylon_orbit()
                self.trigger(Transitions.TransitEndangered_to_DestinationPylonUnknown)
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
            self.trigger(Transitions.PylonTargeted_to_OrbitTargeted)

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
        # do driving stuff

    def is_object_detection_data_available(self):
        return self.object_detector_result is not None

    def start_state_machine(self):
        """
        State: Start
        :return:
        """
        self._logger.debug("Starting State Machine...")
        self.trigger(Transitions.Start_to_DestinationPylonUnknown.name)

    # Node method implementations
    def _start_up(self):
        self.__object_detector_receiver = Receiver("OBJECT_DETECTOR")
        self.__uart_output_sender = Sender(self._node_config_name)

    def _progress(self):
        # self.object_detector_result = self.__object_detector_receiver.receive()

        # test data
        self.object_detector_result = self._create_fake_data()

        current_state_name = self._current_state
        trigger_for_next_state = self._state_machine.get_triggers(current_state_name)
        internal_trigger_for_current_state = [trigger for trigger in trigger_for_next_state if "internal_" in trigger]
        self.trigger(internal_trigger_for_current_state[0])

        # fetch data
        # forward to state
        # analyze data + try to make transition
        # if this fails repeat with next incoming data

        # https://github.com/pytransitions/transitions#automatic-transitions-for-all-states

    def _shut_down(self):
        self.__object_detector_receiver.close()
        self.__uart_output_sender.close()

    @staticmethod
    def _create_fake_data() -> ObjectDetectorResult:
        estimated_pylon = DetectedObject(
            object_type=DetectedObjectType.pylon,
            bounding_box=BoundingBox.of_rectangle_by_center(center=Point(12, 40), width=100, height=500),
            distance=Distance(value=12.5, measured=False),
            relative_objects=List[None]
        )
        measured_pylon = DetectedObject(
            object_type=DetectedObjectType.pylon,
            bounding_box=BoundingBox.of_rectangle_by_center(center=Point(1920 / 2, 1080 / 2), width=100, height=500),
            distance=Distance(value=12.5, measured=True),
            relative_objects=List[None]
        )
        detected_objects = [estimated_pylon, measured_pylon]
        object_detector_result = ObjectDetectorResult(detected_objects)

        return object_detector_result
