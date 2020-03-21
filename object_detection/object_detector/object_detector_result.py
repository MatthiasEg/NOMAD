from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List
from object_detection.bounding_box import BoundingBox


class DetectedObjectType(Enum):
    Pylon = 0
    SquareTimber = 1


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
    IN_FRONT = 0
    BEHIND = 1
    RIGHT = 2
    LEFT = 3


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

    def __init__(self, object_type: DetectedObjectType, bounding_box: BoundingBox, distance: Distance, relative_objects: List[RelativeObject] = []):
        self._object_type: DetectedObjectType = object_type
        self._bounding_box: BoundingBox = bounding_box
        self._distance: Distance = distance  # nullable
        self._relative_objects: List[RelativeObject] = relative_objects

    def relative_detected_objects_from_relative_type(self, relative_type: RelativeObjectType) -> List[DetectedObject]:
        if len(list(self._relative_objects)) == 0:
            empty_list: List[DetectedObject] = []
            return empty_list
        relative_objects_matching_relative_type = [relative_object for relative_object in self.relative_objects if relative_object.relative_type == relative_type]
        detected_objects_matching_relative_type: List[DetectedObject] = []

        for relative_object in relative_objects_matching_relative_type:
            detected_objects_matching_relative_type.append(relative_object.detected_object)
        return detected_objects_matching_relative_type

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

    def get_most_right_pylon(self) -> DetectedObject:
        if self.has_pylons():
            most_right_x = 0
            most_right_pylon = 0
            pylons = self.get_pylons_only()
            for pylon in pylons:
                if most_right_x < pylon.bounding_box.shape.centroid.x:
                    most_right_x = pylon.bounding_box.shape.centroid.x
                    most_right_pylon = pylon
            return most_right_pylon
        else:
            raise Exception(f'Cannot get most right pylon, as there is no pylon! DetectedObjects are: {self._detected_objects}')

    def has_pylons(self) -> bool:
        pylons = self.get_pylons_only()
        return len(pylons) > 0

    def get_pylons_only(self) -> List[DetectedObject]:
        return [detected_object for detected_object in self._detected_objects if detected_object.object_type == DetectedObjectType.Pylon]

    @property
    def get_detected_objects(self) -> List[DetectedObject]:
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
