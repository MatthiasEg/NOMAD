from typing import List

from cv2 import cv2
from shapely.geometry import Point

from object_detection.bounding_box import BoundingBox
import numpy as np


def _extract_bounding_boxes(frame_threshed_red) -> List[BoundingBox]:
    bounding_boxes_of_red_objects: List[BoundingBox] = []
    contours, hierarchy = cv2.findContours(frame_threshed_red, 1, 2)
    for contour in contours:
        min_x, min_y, width, height = cv2.boundingRect(contour)
        bounding_boxes_of_red_objects.append(
            BoundingBox.of_rectangle_by_min_point(Point(min_x, min_y), width, height))
    return bounding_boxes_of_red_objects


class PylonBoundingBoxAdjuster:
    _LOWER_RED_MIN = np.array([0, 100, 100], np.uint8)
    _LOWER_RED_MAX = np.array([10, 255, 255], np.uint8)
    _UPPER_RED_MIN = np.array([160, 100, 100], np.uint8)
    _UPPER_RED_MAX = np.array([179, 255, 255], np.uint8)

    def __init__(self, frame):
        _frame_threshed_red = self._filter_red(frame)
        self._bounding_boxes_of_red_objects = _extract_bounding_boxes(_frame_threshed_red)

    def _filter_red(self, frame):
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame_threshed1 = cv2.inRange(hsv_img, self._LOWER_RED_MIN, self._LOWER_RED_MAX)
        frame_threshed2 = cv2.inRange(hsv_img, self._UPPER_RED_MIN, self._UPPER_RED_MAX)
        frame_threshed_red = cv2.bitwise_or(frame_threshed1, frame_threshed2)

        # close gaps in red objects
        kernel = np.ones((5, 5), np.uint8)
        frame_threshed_red = cv2.morphologyEx(frame_threshed_red, cv2.MORPH_CLOSE, kernel)
        frame_threshed_red = cv2.bitwise_not(frame_threshed_red)
        return frame_threshed_red

    def adjust(self, pylon_bounding_box: BoundingBox) -> BoundingBox:
        min_area = pylon_bounding_box.area * 0.1
        max_area = pylon_bounding_box.area * 0.5
        biggest_red_object_bounding_box: BoundingBox = None
        for bounding_box_red_object in self._bounding_boxes_of_red_objects:
            if bounding_box_red_object.intersects(
                    pylon_bounding_box) and min_area <= bounding_box_red_object.area <= max_area:
                if biggest_red_object_bounding_box is None:
                    biggest_red_object_bounding_box = bounding_box_red_object
                elif biggest_red_object_bounding_box.area < bounding_box_red_object.area:
                    biggest_red_object_bounding_box = bounding_box_red_object

        if biggest_red_object_bounding_box is None:
            return pylon_bounding_box

        return BoundingBox.of_rectangle(biggest_red_object_bounding_box.min_x, pylon_bounding_box.min_y,
                                        biggest_red_object_bounding_box.max_x, pylon_bounding_box.max_y)
