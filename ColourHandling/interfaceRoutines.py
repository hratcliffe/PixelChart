from . import imageExt
from .detect import mergeColours


def reduceColours(image, n_cols, opt=False):

  new_image = mergeColours(image.getImage(opt), n_cols)
  image.setImage(new_image)

