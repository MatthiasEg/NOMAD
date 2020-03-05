from communication.node import Node
from transitions import Machine, State


class SteeringCommandGenerator(Node):

    def __init__(self, node_config_section: str):
        super().__init__("STEERING_COMMAND_GENERATOR")
        self.__states = [
            State(name='destination_pylon_unknown', on_exit=['exit_destination_pylon_unknown']),
            State(name='pylon_targeted', on_exit=['exit_start']),
            State(name='orbit_targeted', on_exit=['exit_orbit_targeted']),
            State(name='orbit_entered', on_exit=['exit_orbit_entered']),
        ]

        self.__transitions = [
            {'trigger': '', 'source': 'destination_pylon_unknown', 'dest': 'pylon_targeted'},
            {'trigger': '', 'source': 'pylon_targeted', 'dest': 'orbit_targeted'},
            {'trigger': '', 'source': 'orbit_targeted', 'dest': 'orbit_entered'},
            {'trigger': '', 'source': 'orbit_entered', 'dest': 'destination_pylon_unknown'},
            {'trigger': '', 'source': 'orbit_targeted', 'dest': 'destination_pylon_unknown'},
        ]

        self.__state_machine = Machine(model=self,
                                       states=self.__states,
                                       transitions=self.__transitions,
                                       initial='start')

    def _startUp(self):
        pass

    def _progress(self):
        pass

    def _shutDown(self):
        pass
