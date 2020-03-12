import zmq
import configparser
import logging


class Receiver:

    def __init__(self, node_config_section: str):
        self._load_configuration(node_config_section)
        self._open_subscribe_socket()
        self._received_counter = 0

    def _load_configuration(self, node_config_section: str):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self._host = config.get(node_config_section, 'HOST')
        self._port = config.get(node_config_section, 'PORT')
        self._logger = logging.getLogger(node_config_section + "_RECEIVER")

    def _open_subscribe_socket(self):
        self._socket = zmq.Context().socket(zmq.SUB)
        self._socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self._socket.connect("tcp://%s:%s" % (self._host, self._port))
        self._logger.info("connect to host: tcp://%s:%s" % (self._host, self._port))

    def receive(self):
        py_object = self._socket.recv_pyobj()
        self._received_counter += 1
        self._logger.debug("received (%s): %s" % (self._received_counter, py_object))
        return py_object

    def close(self):
        self._socket.close()
        self._logger.info("disconnect from host: tcp://%s:%s" % (self._host, self._port))
