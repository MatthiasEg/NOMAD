from typing import List
import numpy as np

from object_detection.object_detector.object_detector_result import ObjectDetectorResult, DetectedObject, RelativeObjectType
from util.pixel_grid_nomad import PixelGridNomad, GridArea


class DangerZone:
    _width: int = 160
    _length: float

    def __init__(self, pixel_grid: PixelGridNomad) -> None:
        self._pixel_grid = pixel_grid

    def is_relevant(self, all_pylons: List[DetectedObject], targeted_pylon: DetectedObject) -> bool:
        self._length = targeted_pylon.distance.value
        max_diagonal_value: float = np.sqrt(self._length ** 2 + self._width ** 2)

        all_pylons_left_frame_side = self._pixel_grid.filter_pylons_of_area(all_pylons, GridArea.LEFT)

        left_pylons_without_targeted_pylon: List[DetectedObject] = [pylon for pylon in all_pylons_left_frame_side if pylon != targeted_pylon]

        left_relevant_pylons_compared_to_length_and_width: List[DetectedObject] = [pylon for pylon in left_pylons_without_targeted_pylon if
                                                                                   (pylon.distance.value <= max_diagonal_value)
                                                                                   and (pylon in targeted_pylon.relative_detected_objects_from_relative_type(
                                                                                       RelativeObjectType.IN_FRONT))]
        if len(left_relevant_pylons_compared_to_length_and_width) != 0:
            return True
        else:
            return False
