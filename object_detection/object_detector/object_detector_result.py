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
        self.value = value
        self.measured = measured

    def __str__(self):
        return "Distance: [value='%s', measured='%s']" % (self.value, self.measured)


class RelativeObjectType(Enum):
    in_front = 0
    behind = 1
    right = 2
    left = 3


class RelativeObject:
    def __init__(self, detected_object: DetectedObject, relative_type: RelativeObjectType):
        self.detected_object = detected_object
        self.relative_type = relative_type

    def __str__(self):
        return "RelativeObject: [detected_object='%s', relative_type='%s']" % (self.detected_object, self.relative_type)


class DetectedObject:
    def __init__(self, object_type: DetectedObjectType, bounding_box: BoundingBox, distance: Distance,
                 relative_objects: List[RelativeObject]):
        self.object_type = object_type
        self.bounding_box = bounding_box
        self.distance = distance  # nullable
        self.relative_objects = relative_objects

    def __str__(self):
        relative_objects_string_representation = ""
        for relative_object in self.relative_objects:
            relative_objects_string_representation += str(relative_object)
        return "DetectedObject: [type='%s', boundingBox='%s', distance='%s', " \
               "relative_objects_string_representation='%s']" % \
               (self.object_type, self.bounding_box, self.distance, relative_objects_string_representation)


class ObjectDetectorResult:
    def __init__(self, detected_objects):
        self.timestamp = datetime.timestamp(datetime.now())
        self.detected_objects = detected_objects

    def __str__(self):
        detected_objects_string_representation = ""
        for detected_object in self.detected_objects:
            detected_objects_string_representation += str(detected_object)
        return "ObjectDetectorResult: [timestamp='%s', detected_objects_string_representation='%s']" % (
            self.timestamp, detected_objects_string_representation)
