import configparser
import time
import logging
from abc import ABC, abstractmethod


class Node(ABC):

    def __init__(self, node_config_section: str):
        self.__load_configuration(node_config_section)

    def __load_configuration(self, node_config_section: str):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.__sleep_time_seconds = config.getfloat(node_config_section, 'SLEEP_TIME_MS') / 1000
        self.__logger = logging.getLogger(node_config_section)

    def start(self):
        self.__logger.info("starting ...")
        self._start_up()
        try:
            while True:
                self._progress()
                time.sleep(self.__sleep_time_seconds)
        finally:
            self.__logger.info("stopping ...")
            self._shut_down()

    # sender and receiver connections are built
    @abstractmethod
    def _start_up(self):
        pass

    # node specific logic
    @abstractmethod
    def _progress(self):
        pass

    # sender and receiver connections are closed
    @abstractmethod
    def _shut_down(self):
        pass
