from enum import Enum
import logging

class SituationAnalyzer: 
  logger = logging.getLogger("SituationAnalyzer")

  def analyze(self, centredPylon, obstacleDetectorResult):
    if(centredPylon != None):
      return self.analyzeWithCentredPylon(centredPylon, obstacleDetectorResult)
    else:
      return self.analyzeWithoutCentredPylon(obstacleDetectorResult)

  def analyzeWithCentredPylon(self, centredPylon, obstacleDetectorResult):
    if(obstacleDetectorResult.contactBottom):
      if(obstacleDetectorResult.distanceTop==obstacleDetectorResult.distanceBottom):
        intersectingEdge = obstacleDetectorResult.getEdgeWhichIntersectRectangle(centredPylon.boundingBox)
        if(intersectingEdge != None):
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

  def analyzeWithoutCentredPylon(self, obstacleDetectorResult):
    if(obstacleDetectorResult.contactBottom):
      if(obstacleDetectorResult.distanceTop==obstacleDetectorResult.distanceBottom):
        self.logger.debug("Unknown Situation")
        return Situation.ignore #roadside use cases currently not implemented
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