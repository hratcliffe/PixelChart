class ImagePayload():
  def __init__(self, sz):
    self.sz = sz


class ColourPayload():
  def __init__(self, n_cols, opts={}):
    self.n_cols = n_cols
    self.opts = opts
