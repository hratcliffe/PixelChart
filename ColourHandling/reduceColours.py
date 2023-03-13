from .replace import *

from .colourDistances import calculateDistance


def combineColours(image, colourList, finalColour):
  """Combine the colours given by colourList to a single value, finalColour
    and return the image with this applied"""
  return combineColoursFromList(image, colourList, finalColour)


def getSimilarColours(colour, allColours, n_cols=10):
    """Returnt the 'n_cols' closest colours to 'colour' from 'allColours' """

    dists = [(calculateDistance(colour, item), item) for item in allColours]
    dists = sorted(dists, key=lambda tup:tup[0])
    try:
      # Take only first n_cols, or all if less available
      dists = dists[0:n_cols]
    except:
      pass

    return [item[1] for item in dists]