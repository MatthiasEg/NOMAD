from typing import List, Dict

from communication.node import Node
from transitions import Machine, State
import logging

from communication.receiver import Receiver
from communication.sender import Sender


class SteeringCommandGenerator(Node):
    __node_config_name = "STEERING_COMMAND_GENERATOR"
    __logger = logging.getLogger("SteeringCommandGenerator")

    def __init__(self):
        super().__init__(self.__node_config_name)

        self.__states = [
            State(name='Start'),
            State(name='DestinationPylonUnknown', on_enter=['process_object_detector_data']),
            State(name='PylonTargeted'),
            State(name='OrbitTargeted'),
            State(name='OrbitEntered'),
        ]

        self.__transitions = [
            {'trigger': 'start_state_machine', 'source': 'Start', 'dest': 'DestinationPylonUnknown',
             'conditions': 'is_object_detection_data_available'},
            {'trigger': 'pylon_detected', 'source': 'DestinationPylonUnknown', 'dest': 'PylonTargeted'},
            {'trigger': 'calculate_pylon_number_and_distances', 'source': 'PylonTargeted', 'dest': 'OrbitTargeted'},
            {'trigger': 'methoddummy3', 'source': 'OrbitTargeted', 'dest': 'OrbitEntered'},
            # inverse transitions
            {'trigger': 'methoddummy4', 'source': 'OrbitEntered', 'dest': 'DestinationPylonUnknown'},
            {'trigger': 'methoddummy5', 'source': 'OrbitTargeted', 'dest': 'DestinationPylonUnknown'},
        ]

        self.__state_machine = Machine(model=self,
                                       states=self.__states,
                                       transitions=self.__transitions,
                                       initial='Start')
        self.__state_machine.set_state('Start')

    def is_object_detection_data_available(self):
        return self.object_detector_result is not None

    def start_state_machine(self):
        self.__logger.debug("start state triggered")
        pass

    def process_object_detector_data(self):
        pass

    def get_states(self) -> List[State]:
        return self.__states

    def get_transitions(self) -> List[Dict[str, str]]:
        return self.__transitions

    # Node method implementations
    def _start_up(self):
        self.__object_detector_receiver = Receiver("OBJECT_DETECTOR")
        self.__uart_output_sender = Sender(self.__node_config_name)

    def _progress(self):
        # self.object_detector_result = self.__object_detector_receiver.receive()

        self.object_detector_result = "[contact_top='True', distance_top='230', contact_bottom='False', distance_bottom='400', edges_string_representation='LINESTRING (30 20, 200 40)LINESTRING (32 19, 195 41)']"

        self.__logger.info(f"STATE: {self.__state_machine.get_model_state(self).name}")
        self.start_state_machine()
        self.trigger('start_state_machine')
        self.__logger.info(f"STATE: {self.__state_machine.get_model_state(self).name}")
        self.trigger('pylon_detected')
        self.__logger.info(f"STATE: {self.__state_machine.get_model_state(self).name}")

    def _shut_down(self):
        self.__object_detector_receiver.close()
        self.__uart_output_sender.close()
