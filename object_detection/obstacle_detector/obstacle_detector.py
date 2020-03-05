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
        edge_one = Line(Point(30, 20), Point(200, 40))
        edge_two = Line(Point(32, 19), Point(195, 41))
        obstacle_detector_result = ObstacleDetectorResult(True, 230, False, 400, (edge_one, edge_two))
        self.obstacleDetectorSender.send(obstacle_detector_result)

    def _shutDown(self):
        self.obstacleDetectorSender.close()
