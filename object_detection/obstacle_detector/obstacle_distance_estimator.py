import configparser
import logging
from object_detection.object_detector.object_detector_result import Distance


class ObstacleDistanceEstimator:
    _logger = logging.getLogger("ObstacleDistanceEstimator")
    _FOCAL_LENGTH = 65 # manually calculate with example images 9 pixel height for distance 6m and real height 6cm
    # F = (P x D) /W P: Pixel width, D: distance, W: known width, F: perceived focal lenght =>  (9pixel * 6m) / 0.06m = 900

    def estimate(self, height) -> Distance:
        if height <= 0:
            return -1

        estimated_distance = Distance(self._FOCAL_LENGTH / height, False)
        self._logger.debug(
            "estimated distance: '%s' (by height='%s')" % (estimated_distance, height))
        return estimated_distance

# x * 9px = 6m =>  distance = x * height