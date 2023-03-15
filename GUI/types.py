class ImageStatePayload():
  def __init__(self, sz, n_cols=-1):
    self.sz = sz
    self.n_cols = n_cols


class ImageChangePayload():
  def __init__(self, n_cols, opts={}):
    self.n_cols = n_cols
    self.opts = opts

class ImageCombinePayload():
  def __init__(self, original, new):
    self.original = original
    self.new = new

class PatternPayload():
  def __init__(self, filename, details):
    self.filename = filename
    self.details = details

class ImageSizePayload():
  def __init__(self, wid, ht):
    self.width = wid
    self.height = ht

class ImageEnhancePayload():
  def __init__(self, attr, old, new):
    self.attr = attr
    self.oldValue = old
    self.newValue = new
