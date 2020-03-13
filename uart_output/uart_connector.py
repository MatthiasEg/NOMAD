import logging

from communication.node import Node
from communication.receiver import Receiver


class UartConnector(Node):
    _node_config_name = "UART_CONNECTOR"
    _logger = logging.getLogger("UartConnector")

    def __init__(self):
        super().__init__(self._node_config_name)

    def _start_up(self):
        self._steering_command_generator_receiver = Receiver("STEERING_COMMAND_GENERATOR")

    def _progress(self):
        self._steering_command_generator_result = self._steering_command_generator_receiver.receive()
        # do fancy uart stuff
        self._logger.debug('UartConnector is progressing...')
        pass

    def _shut_down(self):
        self._steering_command_generator_receiver.close()
