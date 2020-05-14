from typing import List
import numpy as np

from object_detection.object_detector.object_detector_result import ObjectDetectorResult, DetectedObject, RelativeObjectType
from util.pixel_grid_nomad import PixelGridNomad, GridArea


class DangerZone:
    _width: int = 160
    _length: float
    _number_of_evaluations: int = 0

    _nearest_dangerous_pylon: DetectedObject
    _dangerous_pylons_current_evaluation: List[DetectedObject] = []

    _distances_to_nearest_dangerous_pylon_all_evaluations: List[float] = []

    def __init__(self, pixel_grid: PixelGridNomad) -> None:
        self._pixel_grid = pixel_grid

    def evaluate_dangerous_pylons(self, all_pylons: List[DetectedObject], targeted_pylon: DetectedObject):
        self._number_of_evaluations += 1
        self._length = targeted_pylon.distance.value
        max_diagonal_value: float = np.sqrt(self._length ** 2 + self._width ** 2)

        all_pylons_left_frame_side = self._pixel_grid.filter_pylons_of_area(all_pylons, GridArea.LEFT)
        left_pylons_without_targeted_pylon: List[DetectedObject] = [pylon for pylon in all_pylons_left_frame_side if pylon != targeted_pylon]

        left_in_front_relevant_pylons_compared_to_diagonal_and_relative_type: List[DetectedObject] = [
            pylon for pylon in left_pylons_without_targeted_pylon if
            (pylon.distance.value <= max_diagonal_value) and
            (pylon in targeted_pylon.relative_detected_objects_from_relative_type(RelativeObjectType.IN_FRONT)) and
            (pylon in targeted_pylon.relative_detected_objects_from_relative_type(RelativeObjectType.LEFT))
        ]
        print(f"left_in_front_relevant_pylons_compared_to_diagonal_and_relative_type: {str(left_in_front_relevant_pylons_compared_to_diagonal_and_relative_type)}")
        self._dangerous_pylons_current_evaluation = left_in_front_relevant_pylons_compared_to_diagonal_and_relative_type
        if len(self._dangerous_pylons_current_evaluation) != 0:
            self._find_nearest_dangerous_pylon()

    def has_dangerous_pylons(self) -> bool:
        """
        Checks if there is a pylon in the danger zone.
        :Dreturn: true if pylon in danger zone, false if not.
        """
        return len(self._dangerous_pylons_current_evaluation) != 0

    def percentage_distance_decrease_between_first_and_last_evaluation(self):
        if len(self._distances_to_nearest_dangerous_pylon_all_evaluations) < 2:
            raise Exception('Not enough evaluations done to calculate percentage distance decrease!')
        else:
            copy_of_evaluated_distances: List[float] = self._distances_to_nearest_dangerous_pylon_all_evaluations.copy()

            last_evaluated_distance = self._distances_to_nearest_dangerous_pylon_all_evaluations.pop()
            first_evaluated_distance = self._distances_to_nearest_dangerous_pylon_all_evaluations.pop(0)

            # restore previous state of all measures distances between nomad and dangerous pylon
            self._distances_to_nearest_dangerous_pylon_all_evaluations = copy_of_evaluated_distances

            if (last_evaluated_distance / first_evaluated_distance) >= 1:
                raise Exception(
                    "Distance to dangerous pylon did not decrease. Maybe it got out of sight and another pylon is now most dangerous pylon and got measured instead.")
            else:
                percentage_distance_decrease = 1 - (last_evaluated_distance / first_evaluated_distance)
                return percentage_distance_decrease

    @property
    def dangerous_pylons(self) -> List[DetectedObject]:
        return self._dangerous_pylons_current_evaluation

    @property
    def number_of_evaluations(self) -> int:
        return self._number_of_evaluations

    @property
    def nearest_dangerous_pylon(self) -> DetectedObject:
        return self._nearest_dangerous_pylon

    @property
    def distances_to_nearest_dangerous_pylon_all_evaluations(self):
        return self._distances_to_nearest_dangerous_pylon_all_evaluations

    def _find_nearest_dangerous_pylon(self):
        if self._dangerous_pylons_current_evaluation is None or len(self._dangerous_pylons_current_evaluation) < 1:
            raise Exception("Cannot find nearest dangerous pylon as there is no pylon in danger zone!")
        else:
            min_distance = min([pylon.distance for pylon in self._dangerous_pylons_current_evaluation])
            nearest_dangerous_pylon = [pylon for pylon in self._dangerous_pylons_current_evaluation if pylon.distance == min_distance]
            self._nearest_dangerous_pylon = nearest_dangerous_pylon.pop()
            self._distances_to_nearest_dangerous_pylon_all_evaluations.append(self._nearest_dangerous_pylon.distance.value)

    def reset(self):
        self._number_of_evaluations = 0
        self._dangerous_pylons_current_evaluation = []
        self._distances_to_nearest_dangerous_pylon_all_evaluations = []
        # noinspection PyTypeChecker
        self._nearest_dangerous_pylon = None
