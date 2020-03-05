import configparser
import logging
from object_detection.object_detector.object_detector_result import Distance


class PylonDistanceEstimator:
    __logger = logging.getLogger("PylonDistanceEstimator")

    def __init__(self):
        self.__load_configuration()

    def __load_configuration(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.__real_width = config.get('PYLON_DISTANCE_ESTIMATOR', 'PYLON_REAL_WIDTH')
        self.__real_height = config.get('PYLON_DISTANCE_ESTIMATOR', 'PYLON_REAL_HEIGHT')

    def estimate(self, width, height) -> Distance:
        estimated_distance = Distance(10, False)
        self.__logger.debug(
            "estimated distance: '%s' (by width='%s', height='%s')" % (estimated_distance, width, height))
        return estimated_distance
