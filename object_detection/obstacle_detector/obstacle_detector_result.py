from typing import List, Optional
from object_detection.bounding_box import BoundingBox
from object_detection.object_detector.object_detector_result import DetectedObject


class ObstacleDetectorResult:

    def __init__(self, obstacles: List[DetectedObject]):
        self._obstacles = obstacles

    @property
    def obstacles(self) -> List[DetectedObject]:
        return self._obstacles

    def get_nearest_obstacle_which_intersects(self, bounding_box: BoundingBox) -> Optional[DetectedObject]:
        nearest_obstacle: Optional[DetectedObject] = None
        for obstacle in self._obstacles:
            if obstacle.bounding_box.intersects(bounding_box):
                if nearest_obstacle is None or obstacle.distance.value < nearest_obstacle.distance.value:
                    nearest_obstacle = obstacle
        return nearest_obstacle

    def __str__(self):
        obstacle_string_representation = ""
        for obstacle in self.obstacles:
            obstacle_string_representation += str(obstacle)
        return "ObstacleDetectorResult: [edges_string_representation='%s']" % obstacle_string_representation
