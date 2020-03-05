from shapely.geometry import Point

from communication.sender import Sender
from communication.node import Node
from object_detection.bounding_box import BoundingBox
from object_detection.pylon_detector.pylon_detector_result import PylonDetectorResult
from object_detection.pylon_detector.pylon_detector_result import Pylon
from object_detection.pylon_detector.pylon_distance_estimator import PylonDistanceEstimator


class PylonDetector(Node):
    __node_config_section = "PYLON_DETECTOR"

    def __init__(self):
        super().__init__(self.__node_config_section)
        self.__pylon_distance_estimator = PylonDistanceEstimator()

    def __create_pylon(self) -> Pylon:
        estimated_distance = self.__pylon_distance_estimator.estimate(100, 50)
        rectangle_center_point = Point(12, 40)
        return Pylon(BoundingBox.of_rectangle_by_center(rectangle_center_point, 100, 500), estimated_distance, True)

    # Node method implementations
    def _start_up(self):
        self.__pylon_detector_sender = Sender(self.__node_config_section)

    def _progress(self):
        pylon_one = self.__create_pylon()
        pylon_two = self.__create_pylon()
        self.__pylon_detector_sender.send(PylonDetectorResult([pylon_one, pylon_two]))

    def _shut_down(self):
        self.__pylon_detector_sender.close()
