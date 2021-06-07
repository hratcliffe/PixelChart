class ImageStatePayload():
  def __init__(self, sz, n_cols=-1):
    self.sz = sz
    self.n_cols = n_cols

  def __str__(self):
    return "ImageState: [sz={}, n_cols={}]".format(self.sz, self.n_cols)
  def __repr__(self):
    return "ImageStatePayload({},{})".format(self.sz, self.n_cols)

  def as_dict(self):
    return {"name":"ImageStatePayload", "sz":self.sz, "n_cols":self.n_cols}

  def to_json(self):
    return self.as_dict()

class ImageChangePayload():
  def __init__(self, n_cols, opts={}):
    self.n_cols = n_cols
    self.opts = opts

  def __str__(self):
    return "ImageChange: [n_cols={}, opts={}]".format(self.n_cols, self.opts)
  def __repr__(self):
    return "ImageChangePayload({},{})".format(self.n_cols, self.opts)

  def as_dict(self):
    return {"name":"ImageChangePayload", "n_cols":self.n_cols, "opts":self.opts}

  def to_json(self):
    return self.as_dict()

class PatternPayload():
  def __init__(self, filename, details):
    self.filename = filename
    self.details = details

  def __str__(self):
    return "Pattern: [filename={}, details={}]".format(self.filename, self.details)
  def __repr__(self):
    return "PatternPayload({},{})".format(self.filename, self.details)

  def as_dict(self):
    return {"name":"PatternPayload", "filename":self.filename, "details":self.details}

  def to_json(self):
    return self.as_dict()

class ImageSizePayload():
  def __init__(self, wid, ht):
    self.width = wid
    self.height = ht

  def __str__(self):
    return "ImageSize: [width={}, height={}]".format(self.width, self.height)
  def __repr__(self):
    return "ImageSizePayload({},{})".format(self.width, self.height)

  def as_dict(self):
    return {"name":"ImageSizePayload", "width":self.width, "height":self.height}

  def to_json(self):
    return self.as_dict()

class ColourRemapPayload():
  def __init__(self, brand, remap):
    self.brand = brand
    self.remap = remap

  def __str__(self):
    return "ColourRemap: [brand={}, remap={}]".format(self.brand, self.remap)
  def __repr__(self):
    return "ColourRemapPayload({},{})".format(self.brand, self.remap)

  def as_dict(self):
    return {"name":"ColourRemapPayload", "brand":self.brand, "remap":self.remap}

  def to_json(self):
    return self.as_dict()


