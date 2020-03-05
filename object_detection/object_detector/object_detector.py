from communication.receiver import Receiver
from communication.sender import Sender
from object_detection.bounding_box import BoundingBox
from object_detection.object_detector.situation_analyzer import SituationAnalyzer
from communication.node import Node
import configparser


class ObjectDetector(Node):
    __node_config_section = "OBJECT_DETECTOR"

    def __init__(self):
        super().__init__(self.__node_config_section)
        self.__situation_analyzer = SituationAnalyzer()
        self.__ultra_sonic_range = ObjectDetector.__load_ultra_sonic_range()

    # Node method implementations
    def _start_up(self):
        self.__pylon_detector_receiver = Receiver("PYLON_DETECTOR")
        self.__obstacle_detector_receiver = Receiver("OBSTACLE_DETECTOR")
        self.__object_detector_sender = Sender(self.__node_config_section)

    def _progress(self):
        pylon_detector_result = self.__pylon_detector_receiver.receive()
        obstacle_detector_result = self.__obstacle_detector_receiver.receive()
        centred_pylon = pylon_detector_result.get_any_pylon_which_intersects(self.__ultra_sonic_range)
        self.__situation_analyzer.analyze(centred_pylon, obstacle_detector_result)

    def _shut_down(self):
        self.__pylon_detector_receiver.close()
        self.__obstacle_detector_receiver.close()
        self.__object_detector_sender.close()

    @staticmethod
    def __load_ultra_sonic_range():
        config = configparser.ConfigParser()
        config.read('config.ini')
        min_x = config.getint('ULTRASONIC_RECTANGLE_RANGE', 'MIN_X')
        min_y = config.getint('ULTRASONIC_RECTANGLE_RANGE', 'MIN_Y')
        max_x = config.getint('ULTRASONIC_RECTANGLE_RANGE', 'MAX_X')
        max_y = config.getint('ULTRASONIC_RECTANGLE_RANGE', 'MAX_Y')
        return BoundingBox.of_rectangle(min_x, min_y, max_x, max_y)
