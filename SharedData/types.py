class ImageStatePayload():
  def __init__(self, sz, n_cols=-1):
    self.sz = sz
    self.n_cols = n_cols


class ImageChangePayload():
  def __init__(self, n_cols, opts={}):
    self.n_cols = n_cols
    self.opts = opts

class PatternPayload():
  def __init__(self, filename, details):
    self.filename = filename
    self.details = details

class ImageSizePayload():
  def __init__(self, wid, ht):
    self.width = wid
    self.height = ht

class ColourRemapPayload():
  def __init__(self, brand, remap):
    self.brand = brand
    self.remap = remap
