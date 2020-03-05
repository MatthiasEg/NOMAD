import zmq
import configparser
import logging


class Receiver:

    def __init__(self, node_config_section):
        self.__loadConfiguration(node_config_section)
        self.__openPullSocket()
        self.receivedCounter = 0

    def __loadConfiguration(self, node_config_section):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.host = config.get(node_config_section, 'HOST')
        self.port = config.get(node_config_section, 'PORT')
        self.logger = logging.getLogger(node_config_section + "_RECEIVER")

    # noinspection PyUnresolvedReferences
    def __openPullSocket(self):
        self.socket = zmq.Context().socket(zmq.SUB)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.socket.connect("tcp://%s:%s" % (self.host, self.port))
        self.logger.info("connect to host: tcp://%s:%s" % (self.host, self.port))

    def receive(self):
        message = self.socket.recv_pyobj()
        self.receivedCounter += 1
        self.logger.debug("received (%s): %s" % (self.receivedCounter, message))
        return message

    def close(self):
        self.socket.close()
        self.logger.info("disconnect from host: tcp://%s:%s" % (self.host, self.port))
