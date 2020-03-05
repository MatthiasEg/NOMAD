import configparser
import time
import logging
from abc import ABC, abstractmethod


class Node(ABC):

    def __init__(self, node_config_section: str):
        self.node_config_section = node_config_section
        self._loadConfiguration(node_config_section)

    def _loadConfiguration(self, node_config_section):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.sleepTimeMS = config.getfloat(node_config_section, 'SLEEP_TIME_MS') / 1000  # convert miliseconds to seconds
        self.logger = logging.getLogger(node_config_section)

    def start(self):
        self.logger.info("starting ...")
        self._startUp()
        try:
            while True:
                self._progress()
                time.sleep(self.sleepTimeMS)
        finally:
            self.logger.info("stopping ...")
            self._shutDown()

    # sender and receiver connections are built
    @abstractmethod
    def _startUp(self):
        pass

    # node specific logic
    @abstractmethod
    def _progress(self):
        pass

    # sender and receiver connections are closed
    @abstractmethod
    def _shutDown(self):
        pass
