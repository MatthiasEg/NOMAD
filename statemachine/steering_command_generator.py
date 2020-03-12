from typing import List, Dict

from communication.node import Node
from transitions import Machine, State
import logging

from communication.receiver import Receiver
from communication.sender import Sender
from object_detection.object_detector.object_detector_result import ObjectDetectorResult
from statemachine.danger_zone import DangerZone
from statemachine.states import States
from statemachine.steering_command_generator_result import SteeringCommandGeneratorResult
from statemachine.transitions_nomad import TransitionsNomad


class SteeringCommandGenerator(Node):
    __node_config_name = "STEERING_COMMAND_GENERATOR"
    __logger = logging.getLogger("SteeringCommandGenerator")

    def __init__(self):
        super().__init__(self.__node_config_name)

        self.current_state = None
        self.__states = [
            State(name=States.Start.name, on_exit=['drive_fictitious_pylon_orbit']),
            State(name=States.DestinationPylonUnknown.name),
            State(name=States.PylonTargeted.name),
            State(name=States.TransitEndangered.name),
            State(name=States.ObstacleDetected.name),
            State(name=States.OrbitTargeted.name),
            State(name=States.OrbitEntered.name),
        ]

        self.__state_machine = Machine(
            model=self,
            states=self.__states,
            transitions=TransitionsNomad.transitions,
            initial=States.Start,
            auto_transitions=False,
            model_attribute='current_state',
            queued=True
        )
        self.__current_steering_result = SteeringCommandGeneratorResult()

    def drive_orbit(self):
        """
        State: OrbitEntered
        :return:
        """
        # drive orbit with radius of 1 meter or 0.5 meter depending of measured distance
        # scan for pylon while driving, if one is detected keep driving until it is centered
        # then drive towards pylon
        self.trigger('OrbitEntered_to_PylonTargeted')
        # if obstacle is detected in front of nomad, goto state obstacle detected
        self.trigger('OrbitEntered_to_ObstacleDetected')
        # if in next frames pylon to the right side is detected drive fi
        self.drive_fictitious_pylon_orbit()
        self.trigger('OrbitEntered_to_DestinationPylonUnknown')
        pass

    def drive_towards_targeted_pylon(self):
        """
        State: OrbitTargeted, TransitEndangered
        :return:
        """
        # if in state
        self.__logger.debug("DRIVING....")
        if self.__state_machine.get_model_state(self) == 'OrbitTargeted':
            # drive towards pylon and measure distance
            # watch out for pylons on right side of targeted pylon

            pass
        elif self.__state_machine.get_model_state(self) == 'TransitEndangered':
            # drive towards pylon
            # measure distance to horizontal axis of pylon in danger zone
            # if obstacle in front of nomad detected and distance < 0.5m
            self.trigger('TransitEndangered_to_ObstacleDetected')

            # if distance to horizontal axis of pylon in danger zone <=1m do drive_fictitious_pylon_orbit
            if False:
                self.drive_fictitious_pylon_orbit()
                self.trigger("TransitEndangered_to_DestinationPylonUnknown")
            pass

    def is_pylon_in_danger_zone(self):
        """
        State: PylonTargeted
        :return:
        """
        # if in danger zone switch to
        self.__logger.debug("Is Pylon in danger zone?")
        danger_zone = DangerZone()
        if danger_zone.is_relevant():
            self.trigger('PylonTargeted_to_TransitEndangered')
        else:
            self.trigger('PylonTargeted_to_OrbitTargeted')

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
        self.trigger('DestinationPylonUnknown_to_PylonTargeted')

    def drive_fictitious_pylon_orbit(self):
        """
        State: on_exit Start
        :return:
        """
        self.__logger.debug("Driving fictitious pylon orbit")
        # do driving stuff

    def is_object_detection_data_available(self):
        return self.object_detector_result is not None

    def start_state_machine(self):
        """
        State: Start
        :return:
        """
        self.__logger.debug("Starting State Machine...")
        self.trigger('Start_to_DestinationPylonUnknown')

    def process_object_detector_data(self):
        pass

    # Node method implementations
    def _start_up(self):
        self.__object_detector_receiver = Receiver("OBJECT_DETECTOR")
        self.__uart_output_sender = Sender(self.__node_config_name)

    def _progress(self):
        # self.object_detector_result = self.__object_detector_receiver.receive()

        # test data
        self.object_detector_result = ObjectDetectorResult("[data]")

        current_state_name = self.current_state
        trigger_for_next_state = self.__state_machine.get_triggers(current_state_name)
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
            distance=Distance(12.5, False),
            relative_objects=List[None]
        )
        measured_pylon = DetectedObject(
            object_type=DetectedObjectType.pylon,
            bounding_box=BoundingBox.of_rectangle_by_center(center=Point(1920/2, 1080/2), width=100, height=500),
            distance=Distance(value=12.5, measured=True),
            relative_objects=List[None]
        )
        detected_objects = [estimated_pylon, measured_pylon]
        object_detector_result = ObjectDetectorResult(detected_objects)

        return object_detector_result
