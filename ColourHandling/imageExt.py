from PIL import Image
from . import detect, replace


# Defines an extended image, which includes all of the stuff
# For ease of use, image is stored in more than one form 
# which is redundant, so only accessors should be used for 
# writes to ensure sync.
# Symbolic info is also in here, such as colour <-> symbol mappings


# TODO store as IDs and convert back to colours on output, so add converter
class imageExt:

#   def __init__(self):
#     self.colourMap = None # Map from colours to symbols
#     self.codeImage = None # Image (preferaby as array of ids)
#     self.runImage = None  # Image as run-length encoded. Stored as list of lists by row
#     self.colourCounts = None # Map from colours to count of pixels
#     self.imSize = (0,0)
#     self.imMode = 'RGB'
    
    
  def __init__(self, image, sz, maps, mode):
    self.colourMap = maps
    self.codeImage = image # TODO check if is ID coded and fi?
    im, counts = extractRunAndCounts(image, sz)
    self.runImage = im
    self.colourCounts = counts
    self.imSize = sz
    self.imMode = mode
    
  def changeImage(self, image, sz):
    """ Change the core image, size or content but NOT colour"""
    self.codeImage = image # TODO check if is ID coded and fi?
    im, counts = extractRunAndCounts(image, sz)
    self.runImage = im
    self.colourCounts = counts
    self.imSize = sz

  def getColourWithMode(self, colourTriplet):
    """Change from given colour into correct form for mode of this image"""
    
    if self.mode == 'RGB':
      colour = colourTriplet
    elif self.mode == 'RGBA':
      a, b, c = colourTriplet
      colour = (a, b, c, 255)
    else:
      colour = colourTriplet
    
    return colour
    
  @classmethod
  def imageFromFile(cls, filename):

    #Open image
    try:
      im = Image.open(filename)
    except:
      print("File not found or could not be opened. Please try again! Sorry!")
      raise ImageReadError()
      return

    # For simplicity, don't use paletted image
    if im.mode == 'P':
      im = im.convert('RGB')
    
    # Get pixel map to modify
    pixels = im.load()
    sz = im.size
    # Identify number of distinct colours and create two way dicts to Ids
    colours = detect.findColours(pixels, sz)
    colourMaps = replace.mapColours(colours)

    # TODO convert from pixel accessor to plain array for further processing
    
    # TODO store as ids?

    return imageExt(pixels, sz, colourMaps, im.mode)

    
    
def extractRunAndCounts(image, im_sz):
  """ Convert from 2-d array of something (ids, colours etc) into 
  run-length encoded version and also capture counts of each 
  value """
  # Input array must be 2-d and indexable as image[i,j]. Content can be
  # anything as long as it's copyable

  ImRLE = []
  colCounts = {}

  # 2-D indexing because we want row-wise result
  # TODO this is running columns first. FIX
  for i in range(im_sz[0]):
    row = []
    last = image[i, 0]
    count = 1
    for j in range(1, im_sz[1]):

      if image[i, j] == last:
        count = count + 1 

      if image[i,j] != last or j==im_sz[1]-1:
        row.append((last, count)) # Add to RLE image
        try:
          colCounts[last] = colCounts[last] + count # Add to cumulative counts
        except:
          colCounts[last] = count # Start cumulative counts
        last = image[i,j] # Reset
        count = 1
    ImRLE.append(row)

  return (ImRLE, colCounts)  



class ImageReadError(Exception):
  pass

