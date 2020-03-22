from typing import List, Optional

from object_detection.bounding_box import BoundingBox
from object_detection.object_detector.object_detector_result import DetectedObject


class PylonDetectorResult:

    def __init__(self, pylons: List[DetectedObject]):
        self._pylons = pylons

    @property
    def pylons(self) -> List[DetectedObject]:
        return self._pylons

    def get_any_pylon_which_intersects(self, bounding_box: BoundingBox) -> Optional[DetectedObject]:
        for pylon in self._pylons:
            if pylon.bounding_box.intersects(bounding_box):
                return pylon
        return None

    def __str__(self):
        pylon_string_representation = ""
        for pylon in self._pylons:
            pylon_string_representation += str(pylon)
        return pylon_string_representation
