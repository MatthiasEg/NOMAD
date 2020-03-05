from enum import Enum
import logging


class SituationAnalyzer:
    logger = logging.getLogger("SituationAnalyzer")

    def analyze(self, centred_pylon, obstacle_detector_result):
        if centred_pylon is not None:
            return self.analyze_with_centred_pylon(centred_pylon, obstacle_detector_result)
        else:
            return self.analyze_without_centred_pylon(obstacle_detector_result)

    def analyze_with_centred_pylon(self, centred_pylon, obstacle_detector_result):
        if obstacle_detector_result.contactBottom:
            if obstacle_detector_result.distanceTop == obstacle_detector_result.distanceBottom:
                intersecting_edge = obstacle_detector_result.getEdgeWhichIntersectRectangle(centred_pylon.boundingBox)
                if intersecting_edge is not None:
                    self.logger.debug("Square timber behind pylon")
                    return Situation.square_timber_behind_pylon
                else:
                    self.logger.debug("Only pylon in front of the vehicle")
                    return Situation.only_pylon_in_front
            else:
                self.logger.debug("Square timber in fron of pylon")
                return Situation.square_timber_in_front_of_pylon
        else:
            self.logger.debug("Only pylon more then 4 meters away")
            return Situation.pylon_far_away

    def analyze_without_centred_pylon(self, obstacle_detector_result):
        if obstacle_detector_result.contactBottom:
            if obstacle_detector_result.distanceTop == obstacle_detector_result.distanceBottom:
                self.logger.debug("Unknown Situation")
                return Situation.ignore  # roadside use cases currently not implemented
            else:
                self.logger.debug("Only square timber in front")
                return Situation.only_square_timber_in_front
        else:
            self.logger.debug("There is no object in front of vehicle")
            return Situation.no_object_in_front


class Situation(Enum):
    no_object_in_front = 0
    pylon_far_away = 1
    only_pylon_in_front = 2
    square_timber_in_front_of_pylon = 3
    only_square_timber_in_front = 4
    square_timber_behind_pylon = 5
    ignore = 6
