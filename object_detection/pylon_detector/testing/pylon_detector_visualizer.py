from typing import List

import cv2

from camera_sensorinput.read_camera import ReadCamera
from communication.receiver import Receiver
from communication.node import Node
from object_detection.object_detector.object_detector_result import DetectedObject, DetectedObjectType


class PylonDetectorVisualizer(Node):
    _node_config_section = "PYLON_DETECTOR_VISUALIZER"

    def __init__(self):
        super().__init__(self._node_config_section)
        self._sensor_input_camera = ReadCamera()

    def cvDrawBoxes(self, pylons: List[DetectedObject], frame):
        for pylon in pylons:
            xmin = int(pylon.bounding_box.min_x)
            ymin = int(pylon.bounding_box.min_y)
            xmax = int(pylon.bounding_box.max_x)
            ymax = int(pylon.bounding_box.max_y)
            pt1 = (xmin, ymin)
            pt2 = (xmax, ymax)
            cv2.rectangle(frame, pt1, pt2, (0, 255, 0), 1)

            type_decription = "Unknown:"
            if pylon.object_type == DetectedObjectType.Pylon:
                type_decription = "Pylon:"

            cv2.putText(frame, type_decription,
                        (pt1[0], pt1[1] - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        [0, 255, 0], 2)
            cv2.putText(frame, str(pylon.distance),
                        (pt1[0], pt1[1] - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        [0, 255, 0], 2)
            cv2.putText(frame, "Probability [" + str(pylon.probability) + "]",
                        (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        [0, 255, 0], 2)
        return frame

    def _start_up(self):
        self._pylon_detector_receiver = Receiver("PYLON_DETECTOR")

    def _progress(self):
        frame_read = self._sensor_input_camera.get_frame()
        frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)
        frame_resized = frame_rgb
        frame_resized = cv2.resize(frame_rgb, (832, 832), interpolation=cv2.INTER_LINEAR)
        pylon_detector_result = self._pylon_detector_receiver.receive()
        frame_resized = self.cvDrawBoxes(pylon_detector_result.pylons, frame_resized)
        frame_resized = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        cv2.imshow('Pylon_Detector_Visualizer', frame_resized)
        cv2.waitKey(3)

    def _shut_down(self):
        self._pylon_detector_receiver.close()
