from communication.receiver import Receiver
from communication.sender import Sender
from object_detection.object_detector.situation_analyzer import SituationAnalyzer
from object_detection.object_detector.object_detector_result import Distance
from object_detection.object_detector.object_detector_result import DetectedObject
from object_detection.object_detector.object_detector_result import DetectedObjectType
from object_detection.object_detector.object_detector_result import RelativeObject
from object_detection.object_detector.object_detector_result import RelativeObjectType
from communication.node import Node
from geometry.point import Point
from geometry.rectangle import Rectangle
import configparser

class ObjectDetector(Node):
  nodeConfigSection = "OBJECT_DETECTOR"

  def __init__(self):
    super().__init__(self.nodeConfigSection) 
    self.situationAnalyzer = SituationAnalyzer()
    self.ultraSonicRange = self._loadUltraSonicRange()

  def _loadUltraSonicRange(self):
    config = configparser.ConfigParser()                                     
    config.read('config.ini')
    buttomLeft = Point(config.getint('ULTRASONIC_RECTANGLE_RANGE', 'BUTTOM_LEFT_X'), config.getint('ULTRASONIC_RECTANGLE_RANGE', 'BUTTOM_LEFT_Y'))
    topRight = Point(config.getint('ULTRASONIC_RECTANGLE_RANGE', 'TOP_RIGHT_X'), config.getint('ULTRASONIC_RECTANGLE_RANGE', 'TOP_RIGHT_Y'))
    return Rectangle(buttomLeft, topRight)

  def _startUp(self):
    self.pylonDetectorReceiver = Receiver("PYLON_DETECTOR")
    self.obstacleDetectorReceiver = Receiver("OBSTACLE_DETECTOR")
    self.objectDetectorSender = Sender(self.nodeConfigSection)
  
  def _progress(self):
    pylonDetectorResult = self.pylonDetectorReceiver.receive()
    obstacleDetectorResult = self.obstacleDetectorReceiver.receive()
    centredPylon = pylonDetectorResult.getPylonWhichIntersectRectangle(self.ultraSonicRange)
    self.situationAnalyzer.analyze(centredPylon, obstacleDetectorResult)
 
  def _shutDown(self):
    self.pylonDetectorReceiver.close()
    self.obstacleDetectorReceiver.close()
    self.objectDetectorSender.close()