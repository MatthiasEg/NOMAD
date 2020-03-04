from object_detection.obstacle_detector.obstacle_detector_result import ObstacleDetectorResult
from geometry.line import Line
from geometry.point import Point
from communication.sender import Sender
from communication.node import Node

class ObstacleDetector(Node):
  nodeConfigSection = "OBSTACLE_DETECTOR"

  def __init__(self):
    super().__init__(self.nodeConfigSection) 

  def _startUp(self):
    self.obstacleDetectorSender = Sender(self.nodeConfigSection)
  
  def _progress(self):  
    edgeOne = Line(Point(30,20), Point(200,40))
    edgeTwo = Line(Point(32,19), Point(195,41))
    obstacleDetectorResult = ObstacleDetectorResult(True, 230, False, 400, (edgeOne, edgeTwo))
    self.obstacleDetectorSender.send(obstacleDetectorResult)

  def _shutDown(self):
      self.obstacleDetectorSender.close()