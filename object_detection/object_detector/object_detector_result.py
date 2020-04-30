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
        self._value = value  # negative distance means unknown
        self._measured = measured  # true means measured by distance sensors, false means estimated by camera

    @property
    def value(self) -> float:
        return self._value

    @property
    def measured(self) -> bool:
        return self._measured

    def __str__(self):
        return "Distance: [val='%.2f', measured='%s']" % (self._value, self._measured)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Distance) \
               and o._measured == self._measured \
               and o._value == self._value

    def __ne__(self, o: object) -> bool:
        return not self == o


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
        return "RelativeObject: [relative_type='%s']" % (
            self._relative_type)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, RelativeObject) \
               and o.detected_object == self._detected_object \
               and o._relative_type.value == self._relative_type.value

    def __ne__(self, o: object) -> bool:
        return not self == o


class DetectedObject:
    """
    Obstacles or Pylon
    """

    def __init__(self, object_type: DetectedObjectType, bounding_box: BoundingBox, distance: Distance,
                 probability: int,
                 relative_objects: List[RelativeObject]):
        self._object_type: DetectedObjectType = object_type
        self._bounding_box: BoundingBox = bounding_box
        self._distance: Distance = distance  # nullable
        self._probability = probability  # to be really this object
        self._relative_objects: List[RelativeObject] = relative_objects

    def relative_detected_objects_from_relative_type(self, relative_type: RelativeObjectType) -> List[DetectedObject]:
        if self.relative_objects is None or len(list(self._relative_objects)) == 0:
            empty_list: List[DetectedObject] = []
            return empty_list
        relative_objects_matching_relative_type = [relative_object for relative_object in self.relative_objects if
                                                   relative_object.relative_type == relative_type]
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

    @bounding_box.setter
    def bounding_box(self, value):
        self._bounding_box = value

    @property
    def distance(self) -> Distance:
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value

    @property
    def probability(self) -> int:
        return self._probability

    @property
    def relative_objects(self) -> List[RelativeObject]:
        return self._relative_objects

    def add_relative_object(self, other_detected_object: DetectedObject):
        # handle only in_front or behind
        if (other_detected_object.bounding_box.min_x <= self.bounding_box.min_x and
            other_detected_object.bounding_box.max_x >= self.bounding_box.max_x) \
                or (other_detected_object.bounding_box.min_x >= self.bounding_box.min_x and
                    other_detected_object.bounding_box.max_x <= self.bounding_box.max_x):
            self.relative_objects.append(RelativeObject(other_detected_object,
                                                        self._determine_in_front_or_behind(other_detected_object)))
        # handle left
        elif other_detected_object.bounding_box.min_x <= self.bounding_box.min_x:
            self.relative_objects.append(RelativeObject(other_detected_object, RelativeObjectType.LEFT))
            self.relative_objects.append(RelativeObject(other_detected_object,
                                                        self._determine_in_front_or_behind(other_detected_object)))

        # handle right
        elif other_detected_object.bounding_box.max_x >= self.bounding_box.max_x:
            self.relative_objects.append(RelativeObject(other_detected_object, RelativeObjectType.RIGHT))
            self.relative_objects.append(RelativeObject(other_detected_object,
                                                        self._determine_in_front_or_behind(other_detected_object)))

    def _determine_in_front_or_behind(self, other_detected_object: DetectedObject) -> RelativeObjectType:
        if other_detected_object.distance.value <= self.distance.value:
            return RelativeObjectType.IN_FRONT
        else:
            return RelativeObjectType.BEHIND

    def __eq__(self, o: object) -> bool:
        return isinstance(o, DetectedObject) \
               and o._object_type.value == self._object_type.value \
               and o._bounding_box == self._bounding_box \
               and o._distance == self._distance \
               and o._probability == self._probability

    def __ne__(self, o: object) -> bool:
        return not self == o

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
        for detected_object in detected_objects:
            for other_detected_object in detected_objects:
                if detected_object != other_detected_object:
                    detected_object.add_relative_object(other_detected_object)
        self.__pylons = self.get_pylons_only()
        self.__square_timbers = self.get_square_timbers_only()

    def has_pylons(self) -> bool:
        pylons = self.get_pylons_only()
        return len(pylons) > 0

    def has_square_timbers(self) -> bool:
        square_timbers = self.get_square_timbers_only()
        return len(square_timbers) > 0

    def get_pylons_only(self) -> List[DetectedObject]:
        return [detected_object for detected_object in self._detected_objects if
                detected_object.object_type == DetectedObjectType.Pylon]

    def get_square_timbers_only(self) -> List[DetectedObject]:
        return [detected_object for detected_object in self._detected_objects if
                detected_object.object_type == DetectedObjectType.SquareTimber]

    def has_measured_square_timbers(self) -> bool:
        if self.has_square_timbers():
            measured_square_timbers = [square_timber for square_timber in self.get_square_timbers_only() if square_timber.distance.measured]
            return len(measured_square_timbers) != 0
        else:
            return False

    def nearest_square_timber(self) -> DetectedObject:
        if self.has_square_timbers():
            square_timbers = self.get_square_timbers_only()
            measured_distances: List[float] = [square_timber.distance.value for square_timber in square_timbers
                                               if square_timber.distance.measured]
            min_distance = min(measured_distances)

            nearest_square_timber = [square_timber for square_timber in square_timbers if
                                     square_timber.distance.value == min_distance]
            return nearest_square_timber[0]

        else:
            raise Exception('Called nearest_square_timber, when no square timber is available!')

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
