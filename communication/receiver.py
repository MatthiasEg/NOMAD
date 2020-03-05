import zmq
import configparser
import logging


class Receiver:

    def __init__(self, node_config_section: str):
        self.__load_configuration(node_config_section)
        self.__open_subscribe_socket()
        self.__received_counter = 0

    def __load_configuration(self, node_config_section: str):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.__host = config.get(node_config_section, 'HOST')
        self.__port = config.get(node_config_section, 'PORT')
        self.__logger = logging.getLogger(node_config_section + "_RECEIVER")

    def __open_subscribe_socket(self):
        self.__socket = zmq.Context().socket(zmq.SUB)
        self.__socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.__socket.connect("tcp://%s:%s" % (self.__host, self.__port))
        self.__logger.info("connect to host: tcp://%s:%s" % (self.__host, self.__port))

    def receive(self):
        py_object = self.__socket.recv_pyobj()
        self.__received_counter += 1
        self.__logger.debug("received (%s): %s" % (self.__received_counter, py_object))
        return py_object

    def close(self):
        self.__socket.close()
        self.__logger.info("disconnect from host: tcp://%s:%s" % (self.__host, self.__port))
