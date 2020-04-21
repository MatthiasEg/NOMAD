from typing import List

from camera_sensorinput.read_camera import ReadCamera
from communication.sender import Sender
from communication.node import Node
from object_detection.darknet.darknet_wrapper import DarknetWrapper
from object_detection.object_detector.object_detector_result import DetectedObject
from object_detection.pylon_detector.pylon_bounding_box_adjuster import PylonBoundingBoxAdjuster
from object_detection.pylon_detector.pylon_detector_result import PylonDetectorResult
from object_detection.pylon_detector.pylon_distance_estimator import PylonDistanceEstimator


class PylonDetector(Node):
    _node_config_section = "PYLON_DETECTOR"

    def __init__(self):
        super().__init__(self._node_config_section)
        self._pylon_distance_estimator = PylonDistanceEstimator()
        self._sensor_input_camera = ReadCamera()
        self._darknet_wrapper = DarknetWrapper()

    # Node method implementations
    def _start_up(self):
        self._pylon_detector_sender = Sender(self._node_config_section)

    def _progress(self):
        frame_read = self._sensor_input_camera.get_frame()
        detected_pylons: List[DetectedObject] = self._darknet_wrapper.detect_pylons(frame_read)
        for detected_pylon in detected_pylons:
            #detected_pylon.bounding_box = PylonBoundingBoxAdjuster(frame_read).adjust(detected_pylon.bounding_box)
            detected_pylon.distance = self._pylon_distance_estimator.estimate(detected_pylon.bounding_box.width)
        self._pylon_detector_sender.send(PylonDetectorResult(detected_pylons))

    def _shut_down(self):
        self._pylon_detector_sender.close()
