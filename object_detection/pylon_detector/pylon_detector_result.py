from typing import List, Optional

from object_detection.bounding_box import BoundingBox
from object_detection.object_detector.object_detector_result import Distance


class Pylon:

    def __init__(self, bounding_box: BoundingBox, distance: Distance, dangerous: bool):
        self.bounding_box = bounding_box
        self.distance = distance
        self.dangerous = dangerous

    def __str__(self):
        return "(bounding_box='%s', distance='%s', dangerous='%s')" % (
            self.bounding_box, self.distance, self.dangerous)


class PylonDetectorResult:

    def __init__(self, pylons: List[Pylon]):
        self.pylons = pylons

    def get_any_pylon_which_intersects(self, bounding_box: BoundingBox) -> Optional[Pylon]:
        for pylon in self.pylons:
            if pylon.bounding_box.intersects(bounding_box):
                return pylon
        return None

    def __str__(self):
        pylon_string_representation = ""
        for pylon in self.pylons:
            pylon_string_representation += str(pylon)
        return pylon_string_representation
