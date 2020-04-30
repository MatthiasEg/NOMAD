import pickle
from typing import List

from cv2 import cv2

import cv2

from camera_sensorinput.fake_data_reader import FakeDataReader
from camera_sensorinput.read_fake_camera import ReadCamera
from communication.receiver import Receiver
from communication.node import Node
from imu_sensorinput.read_fake_imu import ReadIMU, IMUData
from object_detection.object_detector.object_detector import ObjectDetector
from object_detection.object_detector.object_detector_result import DetectedObject, DetectedObjectType, \
    RelativeObjectType, ObjectDetectorResult
import numpy as np

from sonar_sensorinput.read_fake_sonar import ReadSonar, SonarData
from statemachine.steering_command_generator_result import SteeringCommandGeneratorResult


def draw_detected_objects(frame, detected_objects: List[DetectedObject]):
    cv2.putText(frame, "Number of Detected Objects: " + str(len(detected_objects)), (0, 15), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, [0, 0, 255], 2)

    for detected_object in detected_objects:
        if detected_object.distance.measured:
            color = [255, 0, 0]
        elif detected_object.object_type == DetectedObjectType.SquareTimber:
            color = [255, 0, 255]
        else:
            color = [0, 255, 0]
        # draw bounding box
        min_point = (int(detected_object.bounding_box.min_x), int(detected_object.bounding_box.min_y))
        max_point = (int(detected_object.bounding_box.max_x), int(detected_object.bounding_box.max_y))
        cv2.rectangle(frame, min_point, max_point, color, 1)

        cv2.putText(frame, _determine_object_type_string_representation(detected_object.object_type),
                    (min_point[0], min_point[1] - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    color, 2)

        cv2.putText(frame, str(detected_object.distance), (min_point[0], min_point[1] - 25), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, color, 2)
        cv2.putText(frame, "Probability [" + str(detected_object.probability) + "]", (min_point[0], min_point[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        for relative_object in detected_object.relative_detected_objects_from_relative_type(
                RelativeObjectType.IN_FRONT):
            obj_bbox = detected_object.bounding_box
            rel_obj_bbox = relative_object.bounding_box
            start_point = (int(obj_bbox.center_x()), int(obj_bbox.center_y()))
            end_point = (int(rel_obj_bbox.center_x()), int(rel_obj_bbox.center_y()))
            frame = cv2.arrowedLine(frame, start_point, end_point, [30, 30, 160], 2)
            cv2.putText(frame, "IN_FRONT_OF",
                        (end_point[0], end_point[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0, 0, 255], 2)

        for relative_object in detected_object.relative_detected_objects_from_relative_type(
                RelativeObjectType.BEHIND):
            obj_bbox = detected_object.bounding_box
            rel_obj_bbox = relative_object.bounding_box
            start_point = (int(obj_bbox.center_x()), int(obj_bbox.center_y()))
            end_point = (int(rel_obj_bbox.center_x()), int(rel_obj_bbox.center_y()))
            frame = cv2.arrowedLine(frame, start_point, end_point, [30, 30, 160], 2)
            cv2.putText(frame, "BEHIND",
                        (end_point[0], end_point[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [60, 0, 255], 2)

        for relative_object in detected_object.relative_detected_objects_from_relative_type(
                RelativeObjectType.RIGHT):
            obj_bbox = detected_object.bounding_box
            rel_obj_bbox = relative_object.bounding_box
            start_point = (int(obj_bbox.max_x), int(obj_bbox.min_y + obj_bbox.height / 4))
            end_point = (int(rel_obj_bbox.min_x), int(rel_obj_bbox.min_y + rel_obj_bbox.height / 4))
            frame = cv2.arrowedLine(frame, start_point, end_point, [30, 30, 160], 2)
            cv2.putText(frame, "RIGHT",
                        (end_point[0], end_point[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0, 0, 255], 2)

        for relative_object in detected_object.relative_detected_objects_from_relative_type(
                RelativeObjectType.LEFT):
            obj_bbox = detected_object.bounding_box
            rel_obj_bbox = relative_object.bounding_box
            start_point = (int(obj_bbox.min_x), int(obj_bbox.min_y + obj_bbox.height / 4))
            end_point = (int(rel_obj_bbox.max_x), int(rel_obj_bbox.min_y + rel_obj_bbox.height / 4))
            frame = cv2.arrowedLine(frame, start_point, end_point, [30, 30, 160], 2)
            cv2.putText(frame, "LEFT",
                        (end_point[0], end_point[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0, 0, 255], 2)


def _determine_object_type_string_representation(object_type: DetectedObjectType) -> str:
    if object_type == DetectedObjectType.Pylon:
        return "PYLON"
    elif object_type == DetectedObjectType.SquareTimber:
        return "SQUARE_TIMBER"
    else:
        return "UNKNOWN"


class NomadVisualizer(Node):
    _node_config_section = "VISUALIZER"

    _LOWER_RED_MIN = np.array([0, 100, 100], np.uint8)
    _LOWER_RED_MAX = np.array([10, 255, 255], np.uint8)
    _UPPER_RED_MIN = np.array([160, 100, 100], np.uint8)
    _UPPER_RED_MAX = np.array([179, 255, 255], np.uint8)

    def __init__(self):
        super().__init__(self._node_config_section)
        self._sensor_input_camera = ReadCamera()

    def _start_up(self):
        self.fake_objectresult_reader: FakeDataReader = FakeDataReader("objectresult")
        self._steering_detector_receiver = Receiver("STEERING_COMMAND_GENERATOR")
        self._fake_sonar = ReadSonar()
        self._fake_imu = ReadIMU()

    def _progress(self):
        frame_read = self._sensor_input_camera.get_frame()
        pickle_in = open(self.fake_objectresult_reader.getNextFilePath(), "rb")
        object_detector_result: ObjectDetectorResult = pickle.load(pickle_in)
        steering_command_generator_result: SteeringCommandGeneratorResult = self._steering_detector_receiver.receive()
        sonar_data: SonarData = self._fake_sonar.get_Data()
        imu_data: IMUData = self._fake_imu.get_Data()

        draw_detected_objects(frame_read, object_detector_result.get_detected_objects)

        # draw camera center range on image
        camera_center_range = ObjectDetector.load_camera_center_range()
        min_point = (int(camera_center_range.min_x), int(camera_center_range.min_y))
        max_point = (int(camera_center_range.max_x), int(camera_center_range.max_y))
        # cv2.rectangle(frame_read, min_point, max_point, (255, 0, 0), 1)

        # draw ultrasonic information
        cv2.putText(frame_read, "Ultrasonic Top: " + str(sonar_data.distance_top),
                    (int(camera_center_range.max_x) - 200,
                     int(camera_center_range.max_y) - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, [255, 0, 0], 2)
        cv2.putText(frame_read, "Ultrasonic Bottom: " + str(sonar_data.distance_bottom),
                    (int(camera_center_range.max_x) - 200,
                     int(camera_center_range.max_y) - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, [255, 0, 0], 2)

        # draw imu information
        cv2.putText(frame_read, "Accel x: " + str(imu_data.acc_x),
                    (int(camera_center_range.max_x) - 200,
                     int(camera_center_range.max_y) - 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, [255, 0, 0], 2)
        cv2.putText(frame_read, "Accel y: " + str(imu_data.acc_y),
                    (int(camera_center_range.max_x) - 200,
                     int(camera_center_range.max_y) - 105),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, [255, 0, 0], 2)
        cv2.putText(frame_read, "Accel z: " + str(imu_data.acc_z),
                    (int(camera_center_range.max_x) - 200,
                     int(camera_center_range.max_y) - 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, [255, 0, 0], 2)
        cv2.putText(frame_read, "Gyro x: " + str(imu_data.gyro_x),
                    (int(camera_center_range.max_x) - 200,
                     int(camera_center_range.max_y) - 75),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, [255, 0, 0], 2)
        cv2.putText(frame_read, "Gyro y: " + str(imu_data.gyro_y),
                    (int(camera_center_range.max_x) - 200,
                     int(camera_center_range.max_y) - 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, [255, 0, 0], 2)
        cv2.putText(frame_read, "Gyro z: " + str(imu_data.gyro_z),
                    (int(camera_center_range.max_x) - 200,
                     int(camera_center_range.max_y) - 45),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, [255, 0, 0], 2)

        cv2.putText(frame_read, "state: " + str(steering_command_generator_result.state),
                    (int(camera_center_range.max_x) - 200,
                     int(camera_center_range.max_y) - 210),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, [255, 0, 0], 2)
        cv2.putText(frame_read, "velocity m/s: " + str(steering_command_generator_result.velocity_meters_per_second),
                    (int(camera_center_range.max_x) - 200,
                     int(camera_center_range.max_y) - 195),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, [255, 0, 0], 2)
        cv2.putText(frame_read, "steering angel: " + str(steering_command_generator_result.steering_angel),
                    (int(camera_center_range.max_x) - 200,
                     int(camera_center_range.max_y) - 180),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, [255, 0, 0], 2)
        cv2.putText(frame_read, "driving direction: " + str(steering_command_generator_result.driving_direction),
                    (int(camera_center_range.max_x) - 200,
                     int(camera_center_range.max_y) - 165),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, [255, 0, 0], 2)
        cv2.putText(frame_read, "curve radius centimeters: " + str(steering_command_generator_result.curve_radius_centimeters),
                    (int(camera_center_range.max_x) - 200,
                     int(camera_center_range.max_y) - 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, [255, 0, 0], 2)

        cv2.imshow('NOMAD_Visualizer', frame_read)
        cv2.waitKey(3)

    def _shut_down(self):
        self._steering_detector_receiver.close()
