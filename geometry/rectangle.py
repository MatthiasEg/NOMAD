class Rectangle:

    def __init__(self, bottomLeft, topRight):
        self.bottomLeft = bottomLeft
        self.topRight = topRight

    #Is using Separating Axis Theorem (copied from internet)
    def intersects(self, otherRectangle):
        return not (self.topRight.x < otherRectangle.bottomLeft.x or self.bottomLeft.x > otherRectangle.topRight.x or self.topRight.y < otherRectangle.bottomLeft.y or self.bottomLeft.y > otherRectangle.topRight.y)

    def __str__(self):
        return "(bottomLeft='%s',topRight='%s')" % (self.bottomLeft, self.topRight)