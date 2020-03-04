from datetime import datetime
from enum import Enum

class ObjectDetectorResult:
    def __init__(self, detectedObjects):
        self.timestamp = datetime.timestamp()
        self.detectedObjects = detectedObjects

    def __str__(self):
        detectedObjectsStringRepresentation = ""
        for detectedObject in self.detectedObjects:
            detectedObjectsStringRepresentation += str(detectedObject)
        return "ObjectDetectorResult: [timestamp='%s', detectedObjectsStringRepresentation='%s']" % (self.timestamp, detectedObjectsStringRepresentation)

class DetectedObject:
    def __init__(self, type, boundingBox, distance, relativeObjects):
        self.type = type
        self.boundingBox = boundingBox #could be line or rectangles
        self.distance = distance #nullable
        self.relativeObjects = relativeObjects
    
    def __str__(self):
        relativeObjectsStringRepresentation = ""
        for relativeObject in self.relativeObjects:
            relativeObjectsStringRepresentation += str(relativeObject)
        return "DetectedObject: [type='%s', boundingBox='%s', distance='%s', relativeObjectsStringRepresentation='%s']" % (self.type, self.boundingBox, self.distance, relativeObjectsStringRepresentation)

class DetectedObjectType(Enum):
    pylon = 0
    square_timber = 1

class Distance:
    def __init__(self, value, isMeasured):
        self.value = value
        self.isMeasured = isMeasured
    
    def __str__(self):
        return "Distance: [value='%s', isMeasured='%s']" % (self.value, self.isMeasured)

class RelativeObject:
    def __init__(self, detectedObject, relativeType):
        self.detectedObject = detectedObject
        self.relativeType = relativeType
        
    def __str__(self):
        return "RelativeObject: [detectedObject='%s', relativeType='%s']" % (self.detectedObject, self.relativeType)

class RelativeObjectType(Enum):
    in_front = 0
    behind = 1
    right = 2
    left = 3