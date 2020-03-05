from communication.node import Node
from transitions import Machine, State

from communication.receiver import Receiver
from communication.sender import Sender


class SteeringCommandGenerator(Node):
    __node_config_section = "STEERING_COMMAND_GENERATOR"

    def __init__(self):
        super().__init__(self.__node_config_section)
        self.__states = [
            State(name='destination_pylon_unknown', on_exit=['exit_destination_pylon_unknown']),
            State(name='pylon_targeted', on_exit=['exit_start']),
            State(name='orbit_targeted', on_exit=['exit_orbit_targeted']),
            State(name='orbit_entered', on_exit=['exit_orbit_entered']),
        ]

        self.__transitions = [
            {'trigger': 'methoddummy1', 'source': 'destination_pylon_unknown', 'dest': 'pylon_targeted'},
            {'trigger': 'methoddummy2', 'source': 'pylon_targeted', 'dest': 'orbit_targeted'},
            {'trigger': 'methoddummy3', 'source': 'orbit_targeted', 'dest': 'orbit_entered'},
            {'trigger': 'methoddummy4', 'source': 'orbit_entered', 'dest': 'destination_pylon_unknown'},
            {'trigger': 'methoddummy5', 'source': 'orbit_targeted', 'dest': 'destination_pylon_unknown'},
        ]

        self.__state_machine = Machine(model=self,
                                       states=self.__states,
                                       transitions=self.__transitions,
                                       initial='start')

    # Node method implementations
    def __start_up(self):
        self.__object_detector_receiver = Receiver("OBJECT_DETECTOR")
        self.__uart_output_sender = Sender(self.__node_config_section)

    def __progress(self):
        object_detector_result = self.__object_detector_receiver.receive()

    def __shut_down(self):
        self.__object_detector_receiver.close()
        self.__uart_output_sender.close()
