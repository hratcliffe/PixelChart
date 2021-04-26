from . import symbols
from .image_helpers import imageModeHelper

from PIL import Image

def mapColours(colours):
  """ Create maps between colours and IDs. IDs can then be mapped to symbols"""

  n_colours = len(colours)
  
  fw_map = {}
  bk_map = {}

  for cnt, item in enumerate(colours):
    fw_map[item] = cnt
    bk_map[cnt] = item
  
  return (fw_map, bk_map)
  
  
def replaceColours(originalImage, colourToSymbolMap, colour1, colour2 ):
  """Create the image with colours replaced by symbols"""

  symbols.loadSymbols()
  #Upscale image - scaling dicatated by symbols code
  scale = symbols.getUpscaling()
  sz = originalImage.size
  new_sz = [el * scale for el in sz]

  imNew = Image.new(originalImage.mode, new_sz, colour1)
  pixels = imNew.load()

  for i in range(sz[0]):
    for j in range(sz[1]):
      try:
        symId = colourToSymbolMap[originalImage.getpixel((i,j))]
      except:
        symId = -1
      symbol = symbols.getSymbol(symId)
      
      for loc in symbol.locs:
        pixels[i*scale + loc[0]+1, j*scale + loc[1]+1] = colour2

  # Enclosing box
  for i in range(new_sz[0]):
    pixels[i, 0] = colour2
    pixels[i, new_sz[1]-1] = colour2
  for j in range(new_sz[1]):
    pixels[0, j] = colour2
    pixels[new_sz[0]-1, j] = colour2
    
        
  return imNew

def drawSymbolInPlace(image, symId, colour1, colour2, outline=False):
  """Draw a single symbol in top-left of given image. Fails if image given is too small for symbol"""

  # TODO protect from undersize image

  pixels = image.load()

  symbol = symbols.getSymbol(symId)
  for loc in symbol.locs:
    pixels[loc[0]+1, loc[1]+1] = colour2

  if outline:
    # Enclosing box
    new_sz = image.size
    for i in range(new_sz[0]):
      pixels[i, 0] = colour2
      pixels[i, new_sz[1]-1] = colour2
    for j in range(new_sz[1]):
      pixels[0, j] = colour2
      pixels[new_sz[0]-1, j] = colour2



def addGuide(imageIn, spacing, style, colour):
  """ Add a SINGLE set of guide lines with defined spacing, style and colour
      E.g. adds lines at 0, spacing, spacing*2, spacing*3...
      Image should be supplied as PIL image
      Style is a single character
      Colour should be suitable tuple for image mode
      NB for 'c'ontrast style, range is assumed to be (0,255)"""

  # Guide style None - do nothing
  if(style == 'n') or style not in ['l', 'd', 'p', 'c', 'a']:
    return

  sz = imageIn.size
  image = imageIn.load()

  # Guides placed at multiples of spacing
  for i in range(0, sz[0], spacing):
    for j in range(0, sz[1], spacing):

      # Set central pixel
      image[i,j] = colour
      # Also set additional pixels
      if(style == 'l'):
        line = int(spacing/2)
      elif (style == 'p' or style == 'c'):
        line = int(spacing/4)
      if(style != 'd' and style !='a'):
        for ii in range(-line, line+1):
          try:
            image[i+ii, j] = colour
            image[i, j+ii] = colour
          except:
            pass
      elif style =='a':
        line = int(spacing/3)        
        dist = int(spacing/2)
        for ii in range(-dist, dist):
          if int(ii/line)%2 == 0:
            try:
              image[i+ii, j] = colour
              image[i, j+ii] = colour
            except:
              pass
      # For contrast style, central pixel is contrasting colour
      if(style == 'c'):
        rev_colour = ()
        for k in range(3):
          rev_colour = rev_colour + ( 255-colour[k],)
        for k in range(3, len(colour)):
          rev_colour = rev_colour + (colour[k],)
        image[i, j] = rev_colour

def makeKeyItems(colourToSymbolMap, bg_col, fg_col, mode='RGB', outline=True):
  # Create small images and symbol pictures for each key element

  # Limit items for sanity! 100 only
  limit_num = 100

  els = []
  
  scale_sz = symbols.getUpscaling()
  blob_sz = (scale_sz+1, scale_sz+1)

  cnt = 0
  for key in colourToSymbolMap:
    
    cIm = Image.new(mode, blob_sz, key)
    sIm = Image.new(mode, blob_sz, bg_col)
    drawSymbolInPlace(sIm, colourToSymbolMap[key], bg_col, fg_col, outline=outline)

    els.append([key, colourToSymbolMap[key], cIm, sIm])

    cnt = cnt + 1
    if cnt > limit_num:
      break
  

  return els

def makeSwatchItem(colour, mode='RGB', outline=True):
  # Create swatch in given mode colour

  # Use symbol size as base size
  scale_sz = symbols.getUpscaling()
  blob_sz = (scale_sz+1, scale_sz+1)

  return Image.new(mode, blob_sz, colour)
  
def makeDummy(colourMap):

  width=len(colourMap)
  dummy = Image.new('RGB', (width, 1), (255, 255, 255))
  
  pix = dummy.load()
  cnt = 0
  for item in colourMap:
    pix[cnt, 0] = item
    cnt = cnt+1
    
  imageHelper = imageModeHelper()
  return imageHelper.changeMode(dummy, "RGB", "LAB")
    