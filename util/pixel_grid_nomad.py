from enum import Enum, auto
from typing import Tuple, List

from shapely.geometry import Point
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import cv2.cv2 as cv2
import pylab as pyl
from PIL import Image, ImageDraw

from object_detection.object_detector.object_detector_result import DetectedObject
from statemachine.steering_command_generator_result import DrivingDirection


class GridArea(Enum):
    LEFT = 0
    RIGHT = 1
    TOP = 2
    BOTTOM = 3


class PylonSide(Enum):
    LEFT = 0
    RIGHT = 1
    CENTER_PERFECT = 2


class Resolution(Enum):
    WIDTH = 1920
    HEIGHT = 1080


class PixelGridNomad:
    _x: int = 1920
    _y: int = 1080
    _center_x: int = _x / 2
    _center_y: int = _y / 2
    _x_center_width = 80

    def is_pylon_in_centered_area(self, pylon: DetectedObject) -> bool:
        pylon_x = pylon.bounding_box.center_x()
        return (pylon_x > (self._center_x - self._x_center_width / 2)) and (pylon_x < (self._center_x + self._x_center_width / 2))

    def side_of_pylon(self, pylon: DetectedObject) -> PylonSide:
        pylon_x = pylon.bounding_box.center_x()
        if pylon_x > self._center_x:
            return PylonSide.RIGHT
        elif pylon_x < self._center_x:
            return PylonSide.LEFT
        else:
            return PylonSide.CENTER_PERFECT

    def distances_to_center(self, pylon: DetectedObject) -> Tuple[int, int]:
        """
        Calculates the pixel count between a pylon and the center of the camera.
        :param pylon: The pylon to which the distance in pixel is measured.
        :return:
        x_distance_to_center = negative value, if pylon is to the right of the center, positive value if to the left
        y_distance_to_center = negative value, if pylon further up than the center, positive value if further down
        """
        x_distance_to_center = self._center_x - pylon.bounding_box.center_x()
        y_distance_to_center = self._center_y - pylon.bounding_box.center_y()

        return x_distance_to_center, y_distance_to_center

    @staticmethod
    def get_most_right_pylon(pylons: List[DetectedObject]) -> DetectedObject:
        most_right_x = 0
        most_right_pylon = None
        for pylon in pylons:
            if most_right_x < pylon.bounding_box.center_x():
                most_right_x = pylon.bounding_box.center_x()
                most_right_pylon = pylon
        return most_right_pylon

    @staticmethod
    def get_most_left_pylon(pylons: List[DetectedObject]) -> DetectedObject:
        most_left_x = Resolution.WIDTH
        most_left_pylon = None
        for pylon in pylons:
            if most_left_x > pylon.bounding_box.center_x():
                most_left_x = pylon.bounding_box.center_x()
                most_left_pylon = pylon
        return most_left_pylon

    def has_other_pylons_to_the_right(self, targeted_pylon: DetectedObject, pylons: List[DetectedObject]) -> bool:
        pylons_without_targeted_pylon = [pylon for pylon in pylons if pylon != targeted_pylon]
        other_pylons_to_the_right = self.filter_pylons_of_area(pylons_without_targeted_pylon, GridArea.RIGHT)

        return len(other_pylons_to_the_right) != 0

    def most_centered_pylon(self, pylons: List[DetectedObject]) -> DetectedObject:
        min_x_distance_to_center = self._x
        min_y_distance_to_center = self._y
        min_combined_distance_to_center = min_x_distance_to_center + min_y_distance_to_center
        most_centered_pylon = None

        for pylon in pylons:
            x_distance_to_center = abs(self._center_x - pylon.bounding_box.center_x())
            y_distance_to_center = abs(self._center_y - pylon.bounding_box.center_y())
            combined_distance_to_center = x_distance_to_center + y_distance_to_center
            if combined_distance_to_center < min_combined_distance_to_center:
                min_combined_distance_to_center = combined_distance_to_center
                most_centered_pylon = pylon

        return most_centered_pylon

    def filter_pylons_of_area(self, pylons: List[DetectedObject], area: GridArea) -> List[DetectedObject]:
        if area == GridArea.LEFT:
            return list(filter(lambda pylon: (pylon.bounding_box.center_x() <= self._center_x), pylons))
        elif area == GridArea.RIGHT:
            return list(filter(lambda pylon: (pylon.bounding_box.center_x() >= self._center_x), pylons))
        elif area == GridArea.TOP:
            return list(filter(lambda pylon: (pylon.bounding_box.center_y() >= self._center_y), pylons))
        else:
            return list(filter(lambda pylon: (pylon.bounding_box.center_y() <= self._center_y), pylons))

    def show_test_picture_with_grid(self, step_count: int):
        image = Image.new(mode='L', size=(self._x, self._y), color=255)

        # Draw some lines
        draw = ImageDraw.Draw(image)
        y_start = 0
        y_end = image.height
        step_size = int(image.width / step_count)

        for x in range(0, image.width, step_size):
            line = ((x, y_start), (x, y_end))
            draw.line(line, fill=128)

        x_start = 0
        x_end = image.width

        for y in range(0, image.height, step_size):
            line = ((x_start, y), (x_end, y))
            draw.line(line, fill=128)

        del draw

        image.show()
