import zmq
import configparser
import logging


class Sender:

    def __init__(self, node_config_section: str):
        self._load_configuration(node_config_section)
        self._open_publish_socket()
        self._send_counter = 0

    def _load_configuration(self, node_config_section: str):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self._host = config.get(node_config_section, 'HOST')
        self._port = config.get(node_config_section, 'PORT')
        self._logger = logging.getLogger(node_config_section + "_SENDER")

    def _open_publish_socket(self):
        self._socket = zmq.Context().socket(zmq.PUSH)  # pylint: disable=no-member
        self._socket.bind("tcp://%s:%s" % (self._host, self._port))
        self._logger.info("bind to host: tcp://%s:%s" % (self._host, self._port))

    def send(self, py_object):
        self._socket.send_pyobj(py_object)
        self._send_counter += 1
        self._logger.debug("send (%s): %s" % (self._send_counter, py_object))

    def close(self):
        self._socket.close()
        self._logger.info("unbind from host: tcp://%s:%s" % (self._host, self._port))
