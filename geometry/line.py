class Line:
    
  def __init__(self, startPoint, endPoint):
      self.startPoint = startPoint
      self.endPoint = endPoint

  def intersects(self, rectanlge):
      return True #TODO: implement logic

  def __str__(self):
      return "(startPoint='%s',endPoint='%s')" % (self.endPoint, self.endPoint)