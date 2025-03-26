

class PointMimic:
  """Generic point which addresses as x, y OR 0, 1"""
  def __init__(self, x, y):
    self.x_p = x
    self.y_p = y
  def x(self):
    return self.x_p
  def y(self):
    return self.y_p
  def len(self):
    return 2
  def __getitem__(self, key):
    if key == 0:
      return self.x_p
    elif key == 1:
      return self.y_p
    else:
      raise IndexError("Point index out of range")
  def __repr__(self):
    return "({},{})".format(self.x_p, self.y_p)
