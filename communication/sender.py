import zmq
import configparser
import logging


class Sender:

    def __init__(self, node_config_section: str):
        self.__load_configuration(node_config_section)
        self.__open_publish_socket()
        self.__send_counter = 0

    def __load_configuration(self, node_config_section: str):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.__host = config.get(node_config_section, 'HOST')
        self.__port = config.get(node_config_section, 'PORT')
        self.__logger = logging.getLogger(node_config_section + "_SENDER")

    def __open_publish_socket(self):
        self.__socket = zmq.Context().socket(zmq.PUB)  # pylint: disable=no-member
        self.__socket.bind("tcp://%s:%s" % (self.__host, self.__port))
        self.__logger.info("bind to host: tcp://%s:%s" % (self.__host, self.__port))

    def send(self, py_object):
        self.__socket.send_pyobj(py_object)
        self.__send_counter += 1
        self.__logger.debug("send (%s): %s" % (self.__send_counter, py_object))

    def close(self):
        self.__socket.close()
        self.__logger.info("unbind from host: tcp://%s:%s" % (self.__host, self.__port))
