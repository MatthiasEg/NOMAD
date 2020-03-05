from shapely.geometry import Point
from typing import List, Optional
from object_detection.bounding_box import BoundingBox


class Edge:

    def __init__(self, start: Point, end: Point):
        self.bounding_box = BoundingBox.of_line(start, end)

    def __str__(self):
        return str(self.bounding_box)


class ObstacleDetectorResult:

    def __init__(self, contact_top: bool, distance_top: float, contact_bottom: bool, distance_bottom: float,
                 edges: List[Edge]):
        self.contact_top = contact_top
        self.distance_top = distance_top
        self.contact_bottom = contact_bottom
        self.distance_bottom = distance_bottom
        self.edges = edges

    def get_any_edge_which_intersects(self, bounding_box: BoundingBox) -> Optional[Edge]:
        for edge in self.edges:
            if edge.bounding_box.intersects(bounding_box):
                return edge
        return None

    def __str__(self):
        edges_string_representation = ""
        for edge in self.edges:
            edges_string_representation += str(edge)
        return "ObstacleDetectorResult: [contact_top='%s', distance_top='%s', contact_bottom='%s', " \
               "distance_bottom='%s', edges_string_representation='%s']" % \
               (self.contact_top, self.distance_top, self.contact_bottom, self.distance_bottom,
                edges_string_representation)
