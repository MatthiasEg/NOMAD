import logging
import time
import serial

from communication.node import Node
from communication.receiver import Receiver


class UartConnector(Node):
    _node_config_name = "UART_CONNECTOR"
    _logger = logging.getLogger("UartConnector")
    _BAUDRATE = 57600
    _TX_INTERVAL = 1  # in seconds

    def __init__(self):
        super().__init__(self._node_config_name)

    def _start_up(self):
        self._steering_command_generator_receiver = Receiver("STEERING_COMMAND_GENERATOR")
        self.ser = serial.Serial(
            port='/dev/ttyTHS1',
            baudrate=self._BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
        )

    def _progress(self):
        self._steering_command_generator_result = self._steering_command_generator_receiver.receive()
        while self.ser.is_open:
            self.ser.write(self._steering_command_generator_result.encode())
            self._logger.debug('Sent ' + self._steering_command_generator_result + ' to serial connection')
            time.sleep(self._TX_INTERVAL)

    def _shut_down(self):
        self._steering_command_generator_receiver.close()
        self.ser.close()
