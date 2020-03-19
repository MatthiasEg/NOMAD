from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List
from object_detection.bounding_box import BoundingBox


class DetectedObjectType(Enum):
    pylon = 0
    square_timber = 1


class Distance:
    def __init__(self, value: float, measured: bool):
        self._value = value
        self._measured = measured  # true means measured by distance sensors, false means estimated by camera

    @property
    def value(self) -> float:
        return self._value

    @property
    def measured(self) -> bool:
        return self._measured

    def __str__(self):
        return "Distance: [value='%s', measured='%s']" % (self._value, self._measured)


class RelativeObjectType(Enum):
    in_front = 0
    behind = 1
    right = 2
    left = 3


class RelativeObject:
    def __init__(self, detected_object: DetectedObject, relative_type: RelativeObjectType):
        self._detected_object = detected_object
        self._relative_type = relative_type

    @property
    def detected_object(self) -> DetectedObject:
        return self._detected_object

    @property
    def relative_type(self) -> RelativeObjectType:
        return self._relative_type

    def __str__(self):
        return "RelativeObject: [detected_object='%s', relative_type='%s']" % (
            self._detected_object, self._relative_type)


class DetectedObject:
    """
    Obstacles or Pylon
    """

    def __init__(self, object_type: DetectedObjectType, bounding_box: BoundingBox, distance: Distance,
                 relative_objects: List[RelativeObject]):
        self._object_type = object_type
        self._bounding_box = bounding_box
        self._distance = distance  # nullable
        self._relative_objects = relative_objects

    @property
    def object_type(self) -> DetectedObjectType:
        return self._object_type

    @property
    def bounding_box(self) -> BoundingBox:
        return self._bounding_box

    @property
    def distance(self) -> Distance:
        return self._distance

    @property
    def relative_objects(self) -> List[RelativeObject]:
        return self._relative_objects


def __str__(self):
    relative_objects_string_representation = ""
    for relative_object in self._relative_objects:
        relative_objects_string_representation += str(relative_object)
    return "DetectedObject: [type='%s', boundingBox='%s', distance='%s', " \
           "relative_objects_string_representation='%s']" % \
           (self._object_type, self._bounding_box, self._distance, relative_objects_string_representation)


class ObjectDetectorResult:
    def __init__(self, detected_objects: List[DetectedObject]):
        self._timestamp = datetime.timestamp(datetime.now())
        self._detected_objects = detected_objects

    @property
    def detected_objects(self) -> List[DetectedObject]:
        return self._detected_objects

    @property
    def timestamp(self) -> float:
        return self._timestamp

    def __str__(self):
        detected_objects_string_representation = ""
        for detected_object in self._detected_objects:
            detected_objects_string_representation += str(detected_object)
        return "ObjectDetectorResult: [timestamp='%s', detected_objects_string_representation='%s']" % (
            self._timestamp, detected_objects_string_representation)
