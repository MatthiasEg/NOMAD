from typing import List

from cv2 import cv2

from camera_sensorinput.read_camera import ReadCamera
from communication.receiver import Receiver
from communication.node import Node
from object_detection.object_detector.object_detector import ObjectDetector
from object_detection.object_detector.object_detector_result import DetectedObject, DetectedObjectType, \
    RelativeObjectType
import numpy as np


def draw_detected_objects(frame, detected_objects: List[DetectedObject]):
    cv2.putText(frame, "Number of Detected Objects: " + str(len(detected_objects)), (0, 15), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, [0, 0, 255], 2)

    for detected_object in detected_objects:
        if detected_object.object_type == DetectedObjectType.SquareTimber:
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


class ObjectDetectorVisualizer(Node):
    _node_config_section = "VISUALIZER"

    _LOWER_RED_MIN = np.array([0, 100, 100], np.uint8)
    _LOWER_RED_MAX = np.array([10, 255, 255], np.uint8)
    _UPPER_RED_MIN = np.array([160, 100, 100], np.uint8)
    _UPPER_RED_MAX = np.array([179, 255, 255], np.uint8)

    def __init__(self):
        super().__init__(self._node_config_section)
        self._sensor_input_camera = ReadCamera()

    def _start_up(self):
        self._object_detector_receiver = Receiver("OBJECT_DETECTOR")

    def _progress(self):
        frame_read = self._sensor_input_camera.get_frame()
        object_detector_result = self._object_detector_receiver.receive()

        # hsv_img = cv2.cvtColor(frame_read, cv2.COLOR_BGR2HSV)
        # hsv_img = median = cv2.medianBlur(hsv_img, 5)
        # frame_threshed1 = cv2.inRange(hsv_img, self._LOWER_RED_MIN, self._LOWER_RED_MAX)
        # frame_threshed2 = cv2.inRange(hsv_img, self._UPPER_RED_MIN, self._UPPER_RED_MAX)
        # frame_threshed_red = cv2.bitwise_or(frame_threshed1, frame_threshed2)

        # close gaps in red objects
        # kernel = np.ones((5, 5), np.uint8)
        # frame_threshed_red = cv2.erode(frame_threshed_red, kernel, iterations=2)
        # frame_threshed_red = cv2.dilate(frame_threshed_red, kernel, iterations=5)
        # frame_threshed_red = cv2.bitwise_not(frame_threshed_red)

        draw_detected_objects(frame_read, object_detector_result.get_detected_objects)

        # draw camera center range on image
        camera_center_range = ObjectDetector.load_camera_center_range()
        min_point = (int(camera_center_range.min_x), int(camera_center_range.min_y))
        max_point = (int(camera_center_range.max_x), int(camera_center_range.max_y))
        cv2.rectangle(frame_read, min_point, max_point, (255, 0, 0), 1)

        # draw ultrasonic information
        cv2.putText(frame_read, "Ultrasonic Top: ", (int(camera_center_range.max_x) + 30,
                                                     int(camera_center_range.max_y) - 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, [255, 0, 0], 2)
        cv2.putText(frame_read, "Ultrasonic Bottom: ", (int(camera_center_range.max_x) + 30,
                                                        int(camera_center_range.max_y) - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, [255, 0, 0], 2)

        cv2.imshow('Pylon_Detector_Visualizer', frame_read)
        cv2.waitKey(3)

    def _shut_down(self):
        self._object_detector_receiver.close()
