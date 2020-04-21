from typing import List
from camera_sensorinput.read_camera import ReadCamera
from object_detection.darknet.darknet_wrapper import DarknetWrapper
from object_detection.object_detector.object_detector_result import DetectedObject
from object_detection.obstacle_detector.obstacle_detector_result import ObstacleDetectorResult
from communication.sender import Sender
from communication.node import Node
from object_detection.obstacle_detector.obstacle_distance_estimator import ObstacleDistanceEstimator


class ObstacleDetector(Node):
    _node_config_section = "OBSTACLE_DETECTOR"

    def __init__(self):
        super().__init__(self._node_config_section)

    # Node method implementations
    def _start_up(self):
        self._obstacle_distance_estimator = ObstacleDistanceEstimator()
        self._obstacle_detector_sender = Sender(self._node_config_section)
        self._sensor_input_camera = ReadCamera()
        self._darknet_wrapper = DarknetWrapper()

    def _progress(self):
        frame_read = self._sensor_input_camera.get_frame()
        detected_obstacles: List[DetectedObject] = self._darknet_wrapper.detect_obstacles(frame_read)
        for detected_obstacle in detected_obstacles:
            detected_obstacle.distance = self._obstacle_distance_estimator.estimate(detected_obstacle.bounding_box.height)
        obstacle_detector_result = ObstacleDetectorResult(detected_obstacles)
        self._obstacle_detector_sender.send(obstacle_detector_result)

    def _shut_down(self):
        self._obstacle_detector_sender.close()
