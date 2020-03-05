from shapely.geometry import Point

from object_detection.obstacle_detector.obstacle_detector_result import ObstacleDetectorResult, Edge
from communication.sender import Sender
from communication.node import Node


class ObstacleDetector(Node):
    __node_config_section = "OBSTACLE_DETECTOR"

    def __init__(self):
        super().__init__(self.__node_config_section)

    # Node method implementations
    def _start_up(self):
        self.__obstacle_detector_sender = Sender(self.__node_config_section)

    def _progress(self):
        edge_one = Edge(Point(30, 20), Point(200, 40))
        edge_two = Edge(Point(32, 19), Point(195, 41))
        obstacle_detector_result = ObstacleDetectorResult(True, 230, False, 400, [edge_one, edge_two])
        self.__obstacle_detector_sender.send(obstacle_detector_result)

    def _shut_down(self):
        self.__obstacle_detector_sender.close()
