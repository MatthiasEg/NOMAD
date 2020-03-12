import configparser
import logging
from object_detection.object_detector.object_detector_result import Distance


class PylonDistanceEstimator:
    _logger = logging.getLogger("PylonDistanceEstimator")

    def __init__(self):
        self._load_configuration()

    def _load_configuration(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self._real_width = config.get('PYLON_DISTANCE_ESTIMATOR', 'PYLON_REAL_WIDTH')
        self._real_height = config.get('PYLON_DISTANCE_ESTIMATOR', 'PYLON_REAL_HEIGHT')

    def estimate(self, width, height) -> Distance:
        estimated_distance = Distance(10, False)
        self._logger.debug(
            "estimated distance: '%s' (by width='%s', height='%s')" % (estimated_distance, width, height))
        return estimated_distance
