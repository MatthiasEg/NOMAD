class Line:

    def __init__(self, start_point, end_point):
        self.startPoint = start_point
        self.endPoint = end_point

    def intersects(self, rectanlge):
        return True  # TODO: implement logic

    def __str__(self):
        return "(startPoint='%s',endPoint='%s')" % (self.endPoint, self.endPoint)
