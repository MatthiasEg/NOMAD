from datetime import datetime
from enum import Enum


class ObjectDetectorResult:
    def __init__(self, detected_objects):
        self.timestamp = datetime.timestamp()
        self.detectedObjects = detected_objects

    def __str__(self):
        detected_objects_string_representation = ""
        for detectedObject in self.detectedObjects:
            detected_objects_string_representation += str(detectedObject)
        return "ObjectDetectorResult: [timestamp='%s', detectedObjectsStringRepresentation='%s']" % (
            self.timestamp, detected_objects_string_representation)


class DetectedObject:
    def __init__(self, type, boundingBox, distance, relativeObjects):
        self.type = type
        self.boundingBox = boundingBox  # could be line or rectangles
        self.distance = distance  # nullable
        self.relativeObjects = relativeObjects

    def __str__(self):
        relative_objects_string_representation = ""
        for relativeObject in self.relativeObjects:
            relative_objects_string_representation += str(relativeObject)
        return "DetectedObject: [type='%s', boundingBox='%s', distance='%s', " \
               "relative_objects_string_representation='%s']" % (
                   self.type, self.boundingBox, self.distance, relative_objects_string_representation)


class DetectedObjectType(Enum):
    pylon = 0
    square_timber = 1


class Distance:
    def __init__(self, value, is_measured):
        self.value = value
        self.isMeasured = is_measured

    def __str__(self):
        return "Distance: [value='%s', isMeasured='%s']" % (self.value, self.isMeasured)


class RelativeObject:
    def __init__(self, detected_object, relative_type):
        self.detectedObject = detected_object
        self.relativeType = relative_type

    def __str__(self):
        return "RelativeObject: [detectedObject='%s', relativeType='%s']" % (self.detectedObject, self.relativeType)


class RelativeObjectType(Enum):
    in_front = 0
    behind = 1
    right = 2
    left = 3
