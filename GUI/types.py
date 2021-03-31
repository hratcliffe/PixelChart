class ImagePayload():
  def __init__(self, sz, n_cols=-1):
    self.sz = sz
    self.n_cols = n_cols


class ColourPayload():
  def __init__(self, n_cols, opts={}):
    self.n_cols = n_cols
    self.opts = opts
