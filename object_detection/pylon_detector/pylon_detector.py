from communication.sender import Sender
from communication.node import Node
from object_detection.object_detector.object_detector_result import Distance
from object_detection.pylon_detector.pylon_detector_result import PylonDetectorResult
from object_detection.pylon_detector.pylon_detector_result import Pylon
from object_detection.pylon_detector.pylon_distance_estimator import PylonDistanceEstimator
from geometry.point import Point

class PylonDetector(Node):
  nodeConfigSection = "PYLON_DETECTOR"

  def __init__(self):
    super().__init__(self.nodeConfigSection)
    self.pylonDistanceEstimator = PylonDistanceEstimator()

  def __startUp(self):
    self.pylonDetectorSender = Sender(self.nodeConfigSection)
  
  def __progress(self):
    pylonOne = self.createPylon()
    pylonTwo = self.createPylon()
    self.pylonDetectorSender.send(PylonDetectorResult([pylonOne,pylonTwo]))
        
  def createPylon(self):
    estimatedDistance = Distance(self.pylonDistanceEstimator.estimate(100, 50), False)
    rectangleCenterPoint = Point(12, 40)
    return Pylon(rectangleCenterPoint, 100, 50, estimatedDistance, True)

  def __shutDown(self):
    self.pylonDetectorSender.close()