from __future__ import annotations
from shapely.geometry.base import BaseGeometry
from shapely.geometry import LineString
from shapely.geometry import Point
from shapely.geometry import box


class BoundingBox:

    def __init__(self, shape: BaseGeometry):
        self._shape = shape

    def intersects(self, other: BoundingBox) -> bool:
        return self._shape.intersects(other._shape)

    @staticmethod
    def of_rectangle(min_x: int, min_y: int, max_x: int, max_y: int) -> BoundingBox:
        return BoundingBox(box(min_x, min_y, max_x, max_y))

    @staticmethod
    def of_rectangle_by_center(center: Point, width: int, height: int) -> BoundingBox:
        min_x = center.x - width / 2
        min_y = center.y - height / 2
        max_x = center.x + width / 2
        max_y = center.y + height / 2
        return BoundingBox(box(min_x, min_y, max_x, max_y))

    @staticmethod
    def of_line(start: Point, end: Point) -> BoundingBox:
        return BoundingBox(LineString([start, end]))

    def __str__(self):
        return str(self._shape)
