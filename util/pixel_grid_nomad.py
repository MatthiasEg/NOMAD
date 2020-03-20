from typing import Tuple

from shapely.geometry import Point
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import cv2.cv2 as cv2
import pylab as pyl
from PIL import Image, ImageDraw

from object_detection.object_detector.object_detector_result import DetectedObject
from statemachine.steering_command_generator_result import DrivingDirection


class PixelGridNomad:
    _x: int = 1920
    _y: int = 1080
    _center_x: int = _x / 2
    _center_y: int = _y / 2
    _x_center_width = 80

    def is_pylon_in_centered_area(self, pylon: DetectedObject) -> bool:
        pylon_x = pylon.bounding_box.center_x()
        return (pylon_x > (self._center_x - self._x_center_width / 2)) and (pylon_x < (self._center_x + self._x_center_width / 2))

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
