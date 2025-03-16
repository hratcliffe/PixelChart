# Module defining main colourHandling functions.
# These are the ones we should be using elsewhere in app
from . import imageExt
from .replace import replaceColours, changeColours, addGuide, makeKeyItems, makeDummy, makeSwatchItem
from .symbols import getUpscaling
from .identify import nameColourLAB
from .transform import *
from .reduceColours import combineColours, getSimilarColours, mergeColours


def reduceColours(image, n_cols, emph=None, opt=False):
  """Modify given image to have exactly n_cols distinct colours"""
  new_image = mergeColours(image.getImage(opt), n_cols=n_cols, emph=emph, mode=image.getColourSpace())
  image.setImage(new_image)

def recolour(image, map):
  """Modify given image by changing colours according to the given map"""
  new_image = changeColours(image.getImage(False), map)
  image.setImage(new_image)

def adjustBrightness(image, new_bright):
  """Modify given image brightness to the new value"""
  new_image = modifyBrightness(image.getImage(False), new_bright)
  image.setImage(new_image)

def adjustContrast(image, new_contr):
  """Modify given image contrast to the new value"""
  new_image = modifyContrast(image.getImage(False), new_contr)
  image.setImage(new_image)

def adjustSaturation(image, new_sat):
  """Modify given image saturation to the new value"""
  new_image = modifySaturation(image.getImage(False), new_sat)
  image.setImage(new_image)


def recolourFromList(image, colourList, finalColour):
  """Modify given image by replacing all pixels with values in given colourList
  with a colour value of finalColour """
  new_image = combineColours(image.getImage(False), colourList, finalColour)
  image.setImage(new_image)

def getSimilarColoursFromImage(image, colour):
  """Return a list of the colours in given image which are most
  similar to given colour """
  imageColours = image.colourMap.keys()
  return getSimilarColoursFromList(imageColours, colour)

def getSimilarColoursFromList(imageColours, colour):
  """Return a list of the colours in given imageColours list which are most
  similar to given colour """
  return getSimilarColours(colour, imageColours)


def resizeImage(image, width, height):
  """Modify given image size to new width and height"""
  image.resize(width, height)


def toSymbolicImage(image, guides=None):
  """Return a new image produced by replacing all pixels of given image with
  pattern symbols.
  Guides can be specified as a list of tuples of (spacing, style, colour).
  See replace.addGuides for details
  """
  # TODO doesn't this clobber any passed guides list instead of using it???

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
  """Return a list of the colours in given image, along with their names"""

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
