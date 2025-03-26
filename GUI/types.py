# Minimal POD objects describing actions which cross between GUI elements
# For example, when a new image is loaded, it has a size and a colour count
# which should then be displayed

class ImageStatePayload():
  """Information on general state of image"""
  def __init__(self, sz, n_cols=-1):
    self.sz = sz
    self.n_cols = n_cols


class ImageChangePayload():
  """Information on colour changes image can undergo"""
  def __init__(self, n_cols, opts={}):
    self.n_cols = n_cols
    self.opts = opts

class ImageCombinePayload():
  """Colour combining information"""
  def __init__(self, original, new):
    self.original = original
    self.new = new

class PatternPayload():
  """Information to create a pattern file"""
  def __init__(self, filename, details):
    self.filename = filename
    self.details = details

class ImageSizePayload():
  """Information on image size"""
  def __init__(self, wid, ht):
    self.width = wid
    self.height = ht

class ImageEnhancePayload():
  """Information on an image enhancement"""
  def __init__(self, attr, old, new):
    self.attr = attr
    self.oldValue = old
    self.newValue = new

class ImagePixelRecolourPayload():
  """Information on an pixel-list recolour change"""
  def __init__(self, p_list, new_colour):
    self.pList = p_list
    self.newColour = new_colour

