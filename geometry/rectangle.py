class Rectangle:

    def __init__(self, bottom_left, top_right):
        self.bottomLeft = bottom_left
        self.topRight = top_right

    # Is using Separating Axis Theorem (copied from internet)
    def intersects(self, other_rectangle):
        return not (self.topRight.x < other_rectangle.bottomLeft.x or self.bottomLeft.x > other_rectangle.topRight.x or
                    self.topRight.y < other_rectangle.bottomLeft.y or self.bottomLeft.y > other_rectangle.topRight.y)

    def __str__(self):
        return "(bottomLeft='%s',topRight='%s')" % (self.bottomLeft, self.topRight)
