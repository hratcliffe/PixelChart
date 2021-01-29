

def findColours(pixels, sz):
  """Find all unique colours in an image
     Assuming a true PixelArt Image, these will be identical RGB
     TODO allow small deviation such as slight aliasing etc
  """

  colours = set()

  for i in range(sz[0]):
    for j in range(sz[1]):
      colours.add(pixels[i,j])

  return colours

