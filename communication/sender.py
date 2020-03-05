import zmq
import configparser
import logging


class Sender:

    def __init__(self, node_config_section):
        self._loadConfiguration(node_config_section)
        self._openPushSocket()
        self.sendCounter = 0

    def _loadConfiguration(self, node_config_section):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.host = config.get(node_config_section, 'HOST')
        self.port = config.get(node_config_section, 'PORT')
        self.logger = logging.getLogger(node_config_section + "_SENDER")

    def _openPushSocket(self):
        self.socket = zmq.Context().socket(zmq.PUB)  # pylint: disable=no-member
        self.socket.bind("tcp://%s:%s" % (self.host, self.port))
        self.logger.info("bind to host: tcp://%s:%s" % (self.host, self.port))

    def send(self, message):
        self.socket.send_pyobj(message)
        self.sendCounter += 1
        self.logger.debug("send (%s): %s" % (self.sendCounter, message))

    def close(self):
        self.socket.close()
        self.logger.info("unbind from host: tcp://%s:%s" % (self.host, self.port))
