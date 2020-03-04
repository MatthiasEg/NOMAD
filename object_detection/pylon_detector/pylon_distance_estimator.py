import configparser
import logging

class PylonDistanceEstimator:
    logger = logging.getLogger("PylonDistanceEstimator")

    def __init__(self):
        self._loadConfiguration()

    def _loadConfiguration(self):
        config = configparser.ConfigParser()                                     
        config.read('config.ini')
        self.realWidth = config.get('PYLON_DETECTOR', 'PYLON_REAL_WIDTH')
        self.realHeight = config.get('PYLON_DETECTOR', 'PYLON_REAL_HEIGHT')

    def estimate(self, width, height):
        estimatedDistance = 10
        self.logger.debug("estimated distance: '%s' (by width='%s', height='%s')" % (estimatedDistance, width, height))
        return estimatedDistance