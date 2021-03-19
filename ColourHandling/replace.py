from . import symbols
from PIL import Image

def mapColours(colours):
  """ Create maps between colours and IDs. IDs can then be mapped to symbols"""

  n_colours = len(colours)
  
  fw_map = {}
  bk_map = {}

  #TODO isn't this a dumb replication of IndexOf?
  counter = 0
  for item in colours:
    fw_map[item] = counter
    bk_map[counter] = item
    counter += 1
  
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
      symId = colourToSymbolMap[originalImage.getpixel((i,j))]
      symbol = symbols.getSymbol(symId)
      for k in range(scale):
        pixels[i*scale, j*scale + k] = colour2
        pixels[i*scale+k, j*scale] = colour2
      
      for loc in symbol.locs:
        pixels[i*scale + loc[0]+1, j*scale + loc[1]+1] = colour2
        
  return imNew

