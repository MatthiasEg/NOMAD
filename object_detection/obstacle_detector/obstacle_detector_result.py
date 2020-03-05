class ObstacleDetectorResult:

    def __init__(self, contact_top, distance_top, contact_bottom, distance_bottom, edges):
        self.contactTop = contact_top
        self.distanceTop = distance_top
        self.contactBottom = contact_bottom
        self.distanceBottom = distance_bottom
        self.edges = edges

    def getEdgeWhichIntersectRectangle(self, rectangle):
        for edge in self.edges:
            if edge.intersects(rectangle):
                return edge
        return None

    def __str__(self):
        edges_string_representation = ""
        for edge in self.edges:
            edges_string_representation += str(edge)
        return "ObstacleDetectorResult: [contactTop='%s', distanceTop='%s', contactBottom='%s', distanceBottom='%s', " \
               "edges='%s']" % (self.contactTop, self.distanceTop, self.contactBottom, self.distanceBottom,
                                edges_string_representation)
