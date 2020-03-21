from typing import List
import numpy as np

from object_detection.object_detector.object_detector_result import ObjectDetectorResult, DetectedObject, RelativeObjectType
from util.pixel_grid_nomad import PixelGridNomad, GridArea


class DangerZone:
    _width: int = 160

    def __init__(self, pixel_grid: PixelGridNomad) -> None:
        self._pixel_grid = pixel_grid

    def is_relevant(self, all_pylons: List[DetectedObject], targeted_pylon: DetectedObject) -> bool:
        length_of_danger_zone: float = targeted_pylon.distance.value

        all_pylons_left_frame_side = self._pixel_grid.filter_pylons_of_area(all_pylons, GridArea.LEFT)

        left_pylons_without_targeted_pylon: List[DetectedObject] = [pylon for pylon in all_pylons_left_frame_side if pylon is not targeted_pylon]

        left_relevant_pylons_compared_to_length_and_width: List[DetectedObject] = [pylon for pylon in left_pylons_without_targeted_pylon if
                                                                                   pylon.distance.value <= (
                                                                                       np.sqrt(
                                                                                           length_of_danger_zone ** 2 + self._width ** 2)) and pylon in targeted_pylon.relative_detected_objects_from_relative_type(
                                                                                       RelativeObjectType.IN_FRONT)]
        if len(left_relevant_pylons_compared_to_length_and_width) != 0:
            return True
        else:
            return False
