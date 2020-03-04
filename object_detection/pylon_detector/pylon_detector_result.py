from geometry.rectangle import Rectangle
from geometry.point import Point

class PylonDetectorResult:

    def __init__(self, pylons):
        self.pylons = pylons
        
    def getPylonWhichIntersectRectangle(self, rectangle):
        for pylon in self.pylons:
            if(pylon.boundingBox.intersects(rectangle)):
                return pylon
        return None

    def __str__(self):
        stringRepresentation = ""
        for pylon in self.pylons:
            stringRepresentation += str(pylon)
        return stringRepresentation

class Pylon:

    def __init__(self, rectangleCenterPoint, width, height, distance, isDangerous):
        self.rectangleCenterPoint = rectangleCenterPoint
        self.width = width
        self.height = height
        self.distance = distance
        self.boundingBox = self.createBoundingBox()
        self.isDangerous = isDangerous

    def createBoundingBox(self):
        bottomLeft = Point(self.rectangleCenterPoint.x - self.width/2, self.rectangleCenterPoint.y - self.height/2)
        topRight = Point(self.rectangleCenterPoint.x + self.width/2, self.rectangleCenterPoint.y + self.height/2)
        return Rectangle(bottomLeft, topRight)

    def __str__(self):
     return "(rectangleCenterPoint='%s', width='%s', height='%s', distance='%s', boundingBox='%s')" % (self.rectangleCenterPoint, self.width, self.height, self.distance, self.boundingBox)

