from __future__ import annotations
from shapely.geometry.base import BaseGeometry
from shapely.geometry import LineString
from shapely.geometry import Point
from shapely.geometry import box


class BoundingBox:

    def __init__(self, shape: BaseGeometry):
        self._shape: BaseGeometry = shape
        self._center: Point = shape.centroid
        self._center_x: int = self._center.x
        self._center_y: int = self._center.y
        self._min_x, self._min_y, self._max_x, self._max_y = self._shape.bounds
        self._height = self._max_y - self._min_y
        self._width = self._max_x - self._min_x

    def intersects(self, other: BoundingBox) -> bool:
        return self._shape.intersects(other._shape)

    @staticmethod
    def of_rectangle(min_x: int, min_y: int, max_x: int, max_y: int) -> BoundingBox:
        return BoundingBox(box(min_x, min_y, max_x, max_y))

    @staticmethod
    def of_rectangle_by_center(center: Point, width: int, height: int) -> BoundingBox:
        min_x = int(round(center.x - (width / 2)))
        min_y = int(round(center.y - (height / 2)))
        max_x = int(round(center.x + (width / 2)))
        max_y = int(round(center.y + (height / 2)))
        return BoundingBox(box(min_x, min_y, max_x, max_y))

    @staticmethod
    def of_rectangle_by_min_point(min_point: Point, width: int, height: int) -> BoundingBox:
        min_x = int(round(min_point.x))
        min_y = int(round(min_point.y))
        max_x = int(round(min_point.x + width))
        max_y = int(round(min_point.y + height))
        return BoundingBox(box(min_x, min_y, max_x, max_y))

    @staticmethod
    def of_line(start: Point, end: Point) -> BoundingBox:
        return BoundingBox(LineString([start, end]))

    @property
    def shape(self):
        return self._shape

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def area(self):
        return self._shape.area

    @property
    def max_y(self):
        return self._max_y

    @property
    def max_x(self):
        return self._max_x

    @property
    def min_y(self):
        return self._min_y

    @property
    def min_x(self):
        return self._min_x

    def center_x(self):
        return self._center_x

    def center_y(self):
        return self._center_y

    def center(self):
        return self._center

    def __str__(self):
        return str(self._shape)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, BoundingBox)\
               and o._min_x == self._min_x \
               and o._max_x == self._max_x \
               and o._min_y == self._min_y \
               and o._max_y == self._max_y

    def __ne__(self, o: object) -> bool:
        return not self == o


