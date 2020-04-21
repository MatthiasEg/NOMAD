from typing import List, Optional

from object_detection.bounding_box import BoundingBox
from object_detection.object_detector.object_detector_result import DetectedObject


class PylonDetectorResult:

    def __init__(self, pylons: List[DetectedObject]):
        self._pylons = pylons

    @property
    def pylons(self) -> List[DetectedObject]:
        return self._pylons

    def get_nearest_pylon_which_intersects(self, bounding_box: BoundingBox) -> Optional[DetectedObject]:
        pylons_which_intersects = [pylon for pylon in self._pylons if pylon.bounding_box.intersects(bounding_box)]
        if len(pylons_which_intersects) > 0:
            nearest_pylon = pylons_which_intersects[0]
            for pylon in pylons_which_intersects:
                if pylon.distance.value < nearest_pylon.distance.value:
                    nearest_pylon = pylon
            return nearest_pylon
        else:
            return None

    def __str__(self):
        pylon_string_representation = ""
        for pylon in self._pylons:
            pylon_string_representation += str(pylon)
        return pylon_string_representation
