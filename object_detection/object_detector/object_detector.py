from typing import List

from communication.receiver import Receiver
from communication.sender import Sender
from object_detection.bounding_box import BoundingBox
from object_detection.object_detector.object_detector_result import ObjectDetectorResult, Distance
from communication.node import Node
import configparser

from object_detection.obstacle_detector.obstacle_detector_result import ObstacleDetectorResult
from object_detection.pylon_detector.pylon_detector_result import PylonDetectorResult
from sonar_sensorinput.read_fake_sonar import ReadSonar, SonarData


class ObjectDetector(Node):
    _node_config_section = "OBJECT_DETECTOR"

    def __init__(self):
        super().__init__(self._node_config_section)
        self._camera_center_range = ObjectDetector.load_camera_center_range()

    # Node method implementations
    def _start_up(self):
        self._pylon_detector_receiver = Receiver("PYLON_DETECTOR")
        self._obstacle_detector_receiver = Receiver("OBSTACLE_DETECTOR")
        self._object_detector_sender = Sender(self._node_config_section)
        self._fake_sonar = ReadSonar()

    def _progress(self):
        pylon_detector_result = self._pylon_detector_receiver.receive()
        obstacle_detector_result = self._obstacle_detector_receiver.receive()
        self._set_measured_distance(obstacle_detector_result, pylon_detector_result)
        self._object_detector_sender.send(ObjectDetectorResult(pylon_detector_result.pylons +
                                                               obstacle_detector_result.obstacles))

    def _set_measured_distance(self, obstacle_detector_result: ObstacleDetectorResult,
                               pylon_detector_result: PylonDetectorResult):
        sonar_data: SonarData = self._fake_sonar.get_Data()

        if not sonar_data.contact_top and sonar_data.contact_bottom:  # square timber
            centred_obstacle = obstacle_detector_result.get_nearest_obstacle_which_intersects(self._camera_center_range)
            if centred_obstacle is not None:
                centred_obstacle.distance = Distance(sonar_data.distance_bottom, True)
        elif sonar_data.contact_top and sonar_data.contact_bottom:  # pylon or pylon and square timber
            if sonar_data.distance_top + 5 >= sonar_data.distance_bottom >= sonar_data.distance_top - 15:  # pylon
                centred_pylon = pylon_detector_result.get_nearest_pylon_which_intersects(self._camera_center_range)
                if centred_pylon is not None:
                    centred_pylon.distance = Distance(sonar_data.distance_top, True)
            else:  # pylon behind square_timber
                centred_pylon = pylon_detector_result.get_nearest_pylon_which_intersects(self._camera_center_range)
                if centred_pylon is not None:
                    centred_pylon.distance = Distance(sonar_data.distance_top, True)
                centred_obstacle = obstacle_detector_result.get_nearest_obstacle_which_intersects(
                    self._camera_center_range)
                if centred_obstacle is not None:
                    centred_obstacle.distance = Distance(sonar_data.distance_bottom, True)

    def _shut_down(self):
        self._pylon_detector_receiver.close()
        self._obstacle_detector_receiver.close()
        self._object_detector_sender.close()

    @staticmethod
    def load_camera_center_range():
        config = configparser.ConfigParser()
        config.read('config.ini')
        min_x = config.getint('CAMERA_CENTER_RANGE', 'MIN_X')
        min_y = config.getint('CAMERA_CENTER_RANGE', 'MIN_Y')
        max_x = config.getint('CAMERA_CENTER_RANGE', 'MAX_X')
        max_y = config.getint('CAMERA_CENTER_RANGE', 'MAX_Y')
        return BoundingBox.of_rectangle(min_x, min_y, max_x, max_y)
