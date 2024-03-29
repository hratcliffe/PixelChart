from . import imageExt
from .detect import mergeColours
from .replace import replaceColours, changeColours, addGuide, makeKeyItems, makeDummy, makeSwatchItem
from .symbols import getUpscaling
from .identify import nameColourLAB


def reduceColours(image, n_cols, opt=False):

  new_image = mergeColours(image.getImage(opt), n_cols)
  image.setImage(new_image)


def recolour(image, map):

  new_image = changeColours(image.getImage(False), map)
  image.setImage(new_image)

def resizeImage(image, width, height):

  image.resize(width, height)


def toSymbolicImage(image, guides=None):

  # Guides specified as (spacing, style, colour) tuples or lists

  new_image = imageExt(image.coreImage, image.coreImagePixels, image.colourMap)

  bk_col = image.getColourWithMode((255,255,255))
  fg_col = image.getColourWithMode((0,0,0))
  guide_col = image.getColourWithMode((128,128,128))

  new_image.setImage(replaceColours(image.coreImage, image.colourMap[0], bk_col, fg_col))
  
  scale = getUpscaling()
  
  #default guides are 1 and 10, all solid, grey and black
  guides = [(1, 'l', guide_col), (10, 'l', fg_col)]
  if guides:
    for guide in guides:
      addGuide(new_image.coreImage, guide[0]*scale, guide[1], guide[2])
  
  return new_image

def getKey(image, sort=True):

  bg_col = image.getColourWithMode((255,255,255))
  fg_col = image.getColourWithMode((0,0,0))

  # Create dummy image to simplify conversion to lab. Each pixel is one of the colours, in order left to right
  
  dummyImage = makeDummy(image.colourMap[0])
  dPix = dummyImage.load()

  key = makeKeyItems(image.colourMap[0], bg_col, fg_col, mode=image.coreImage.mode)

  new_key = []
  for item in key:
    name = nameColourLAB(dPix[item[1], 0])
    new_key.append((item[0], item[1], item[2], item[3], name))
  
  if sort:
    # Sort by primary name
    new_key = sorted(new_key, key=lambda x: (x[4][1],x[4][0]) ) 

  return new_key

def makeSwatch(rgb):
  # Make a colour swatch from rgb code
  
  return makeSwatchItem(rgb, mode='RGB')