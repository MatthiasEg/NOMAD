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
    node_config_section = "OBJECT_DETECTOR"

    def __init__(self):
        super().__init__(self.node_config_section)
        self.situationAnalyzer = SituationAnalyzer()
        self.ultraSonicRange = self.__load_ultra_sonic_range()

    def __load_ultra_sonic_range(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        bottom_left = Point(config.getint('ULTRASONIC_RECTANGLE_RANGE', 'BUTTOM_LEFT_X'),
                            config.getint('ULTRASONIC_RECTANGLE_RANGE', 'BUTTOM_LEFT_Y'))
        top_right = Point(config.getint('ULTRASONIC_RECTANGLE_RANGE', 'TOP_RIGHT_X'),
                          config.getint('ULTRASONIC_RECTANGLE_RANGE', 'TOP_RIGHT_Y'))
        return Rectangle(bottom_left, top_right)

    def _startUp(self):
        self.pylonDetectorReceiver = Receiver("PYLON_DETECTOR")
        self.obstacleDetectorReceiver = Receiver("OBSTACLE_DETECTOR")
        self.objectDetectorSender = Sender(self.node_config_section)

    def _progress(self):
        pylon_detector_result = self.pylonDetectorReceiver.receive()
        obstacle_detector_result = self.obstacleDetectorReceiver.receive()
        centred_pylon = pylon_detector_result.getPylonWhichIntersectRectangle(self.ultraSonicRange)
        self.situationAnalyzer.analyze(centred_pylon, obstacle_detector_result)

    def _shutDown(self):
        self.pylonDetectorReceiver.close()
        self.obstacleDetectorReceiver.close()
        self.objectDetectorSender.close()
