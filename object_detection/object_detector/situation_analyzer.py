import logging

from object_detection.object_detector.object_detector_result import DetectedObject, Situation
from object_detection.obstacle_detector.obstacle_detector_result import ObstacleDetectorResult


class SituationAnalyzer:
    _logger = logging.getLogger("SituationAnalyzer")

    def analyze(self, centred_pylon: DetectedObject, obstacle_detector_result: ObstacleDetectorResult) -> Situation:
        if centred_pylon is not None:
            return self.analyze_with_centred_pylon(centred_pylon, obstacle_detector_result)
        else:
            return self.analyze_without_centred_pylon(obstacle_detector_result)

    def analyze_with_centred_pylon(self, centred_pylon: DetectedObject,
                                   obstacle_detector_result: ObstacleDetectorResult) -> Situation:
        if obstacle_detector_result.contact_bottom:
            if obstacle_detector_result.distance_top == obstacle_detector_result.distance_bottom:
                intersecting_edge = obstacle_detector_result.get_any_obstacle_which_intersects(
                    centred_pylon.bounding_box)
                if intersecting_edge is not None:
                    self._logger.debug("Square timber behind pylon")
                    return Situation.square_timber_behind_pylon
                else:
                    self._logger.debug("Only pylon in front of the vehicle")
                    return Situation.only_pylon_in_front
            else:
                self._logger.debug("Square timber in front of pylon")
                return Situation.square_timber_in_front_of_pylon
        else:
            self._logger.debug("Only pylon more then 4 meters away")
            return Situation.pylon_far_away

    def analyze_without_centred_pylon(self, obstacle_detector_result: ObstacleDetectorResult) -> Situation:
        if obstacle_detector_result.contact_bottom:
            if obstacle_detector_result.distance_top == obstacle_detector_result.distance_bottom:
                self._logger.debug("Unknown Situation")
                return Situation.ignore  # roadside use cases currently not implemented
            else:
                self._logger.debug("Only square timber in front")
                return Situation.only_square_timber_in_front
        else:
            self._logger.debug("There is no object in front of vehicle")
            return Situation.no_object_in_front
