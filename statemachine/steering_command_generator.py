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
from statemachine.nomad import Nomad
from statemachine.states_nomad import States, StatesNomad
from statemachine.steering_command_generator_result import SteeringCommandGeneratorResult
from statemachine.transitions_nomad import TransitionsNomad, Transitions


class SteeringCommandGenerator(Node):
    _node_config_name = "STEERING_COMMAND_GENERATOR"
    _logger = logging.getLogger("SteeringCommandGenerator")

    def __init__(self):
        super().__init__(self._node_config_name)

        self._states = StatesNomad().states
        self._transitions = TransitionsNomad().transitions

        self._nomad = Nomad()

        # https://github.com/pytransitions/transitions#automatic-transitions-for-all-states
        self._state_machine = Machine(
            model=self._nomad,
            states=self._states,
            transitions=self._transitions,
            initial="Start",
            auto_transitions=False,
            model_attribute='_state',
            queued=True
        )
        self._current_steering_result = SteeringCommandGeneratorResult()

    # Node method implementations
    def _start_up(self):
        self._object_detector_receiver = Receiver("OBJECT_DETECTOR")
        self._uart_output_sender = Sender(self._node_config_name)

    def _progress(self):
        # self.object_detector_result = self.__object_detector_receiver.receive()

        # test data
        self._nomad.data = self._create_fake_data()

        current_state_name = self._nomad.state
        trigger_for_next_state = self._state_machine.get_triggers(current_state_name)
        internal_trigger_for_current_state = [trigger for trigger in trigger_for_next_state if "internal_" in trigger]
        self._nomad.trigger(internal_trigger_for_current_state[0])

    def _shut_down(self):
        self._object_detector_receiver.close()
        self._uart_output_sender.close()

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
