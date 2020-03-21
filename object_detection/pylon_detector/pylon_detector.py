from typing import List

import cv2
from shapely.geometry import Point

from camera_sensorinput.read_camera import ReadCamera
from communication.sender import Sender
from communication.node import Node
from object_detection.bounding_box import BoundingBox
from object_detection.darknet.darknet_wrapper import DarknetWrapper
from object_detection.pylon_detector.pylon_detector_result import PylonDetectorResult, Pylon
from object_detection.pylon_detector.pylon_distance_estimator import PylonDistanceEstimator


class PylonDetector(Node):
    _node_config_section = "PYLON_DETECTOR"

    def __init__(self):
        super().__init__(self._node_config_section)
        self._pylon_distance_estimator = PylonDistanceEstimator()
        self._sensor_input_camera = ReadCamera()
        self._darknet_wrapper = DarknetWrapper()

    def __create_pylons(self, bounding_boxes: List[BoundingBox]) -> Pylon:
        pylons = []
        for bounding_box in bounding_boxes:
            estimated_distance = self._pylon_distance_estimator.estimate(bounding_box.width, bounding_box.height)
            pylons.append(Pylon(bounding_box, estimated_distance, True))
        return pylons

    # Node method implementations
    def _start_up(self):
        self._pylon_detector_sender = Sender(self._node_config_section)

    def _progress(self):
        frame_read = self._sensor_input_camera.get_frame()
        bounding_boxes = self._darknet_wrapper.detect_pylon_bounding_boxes(frame_read)
        self._pylon_detector_sender.send(PylonDetectorResult(self.__create_pylons(bounding_boxes)))

    def _shut_down(self):
        self._pylon_detector_sender.close()
