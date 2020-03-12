from typing import List, Optional

from object_detection.bounding_box import BoundingBox
from object_detection.object_detector.object_detector_result import Distance


class Pylon:

    def __init__(self, bounding_box: BoundingBox, distance: Distance, dangerous: bool):
        self._bounding_box = bounding_box
        self._distance = distance
        self._dangerous = dangerous

    def __str__(self):
        return "(bounding_box='%s', distance='%s', dangerous='%s')" % (
            self._bounding_box, self._distance, self._dangerous)

    @property
    def bounding_box(self):
        return self._bounding_box


class PylonDetectorResult:

    def __init__(self, pylons: List[Pylon]):
        self._pylons = pylons

    def get_any_pylon_which_intersects(self, bounding_box: BoundingBox) -> Optional[Pylon]:
        for pylon in self._pylons:
            if pylon.bounding_box.intersects(bounding_box):
                return pylon
        return None

    def __str__(self):
        pylon_string_representation = ""
        for pylon in self._pylons:
            pylon_string_representation += str(pylon)
        return pylon_string_representation
