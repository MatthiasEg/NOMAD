import configparser
import time
import logging

class Node:
    
    def __init__(self, nodeConfigSection):
        self.nodeConfigSection = nodeConfigSection
        self._loadConfiguration(nodeConfigSection)

    def _loadConfiguration(self, nodeConfigSection):
        config = configparser.ConfigParser()                                     
        config.read('config.ini')
        self.sleepTimeMS = config.getfloat(nodeConfigSection, 'SLEEP_TIME_MS')/1000 #convert miliseconds to seconds
        self.logger = logging.getLogger(nodeConfigSection)

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
    def _startUp(self): pass

    # node specific logic
    def _progress(self): pass

    # sender and receiver connections are closed
    def _shutDown(self): pass