class ObstacleDetectorResult:

    def __init__(self, contactTop, distanceTop, contactBottom, distanceBottom, edges):
        self.contactTop = contactTop
        self.distanceTop = distanceTop
        self.contactBottom = contactBottom
        self.distanceBottom = distanceBottom
        self.edges = edges

    def getEdgeWhichIntersectRectangle(self, rectangle):
        for edge in self.edges:
            if(edge.intersects(rectangle)):
                return edge
        return None

    def __str__(self):
        edgesStringRepresentation = ""
        for edge in self.edges:
            edgesStringRepresentation += str(edge)
        return "ObstacleDetectorResult: [contactTop='%s', distanceTop='%s', contactBottom='%s', distanceBottom='%s', edges='%s']" % (self.contactTop, self.distanceTop, self.contactBottom, self.distanceBottom, edgesStringRepresentation)
