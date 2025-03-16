#Colour reduction functions - to reduce the number of distinct colours in an image
from .replace import *

from .colourDistances import calculateDistance

from sklearn.cluster import KMeans
from PIL import Image
from math import floor, sqrt

from numpy import ones

def mergeColours(imageIn, n_cols=20, emph=None):
  """Reduce number of colours by clustering. The result will contain exactly n_cols colours. Running this with a large number of end colours is a good first pass at converting a picture into a chart, prior to detailled colour replacements"""

  #If emph is given, upweights the given choice. HOWEVER this does not really change the number of clusters

  # Temporary image as 1-d array of colours
  data = imageIn.getdata()
  sz = imageIn.size

  if emph:
    if emph in ['r', 'g', 'b']:
      weights = calculateWeightsForColour(data, sz, emph)
    elif emph in ['s', 'i']:
      weights = calculateWeightsForChannel(data, sz, emph)
    else:
      raise ValueError("Bad Emphasis Value {}".format(emph))

  # Generate n_cols clusters using 5 random initialisations
  kmeans = KMeans(n_clusters=n_cols, n_init=5, random_state=42)
  if emph:
    kmeans.fit(data, weights)
  else:
    kmeans.fit(data)

  # Report on result
  print("Colour reduction complete after {} iterations. Final inertia {}".format(kmeans.n_iter_, kmeans.inertia_))

  # Create new image where each colour is remapped to the centroid of its cluster.

  new_colours = []
  # Convert from arrays back to tuples
  for item in kmeans.cluster_centers_ :
    new_colours.append (tuple(item))

  # Create new image with replaced colours. Initialise to 0s
  imNew = Image.new(imageIn.mode, sz, (0,0,0))
  pixelsNew = imNew.load()

  # Remap
  for k in range(0, sz[0]*sz[1]-1):
    j = int(floor(k/sz[0]))
    i = int(k - j * sz[0])
    cluster_num = kmeans.labels_[k]
    new_val = [int(c) for c in new_colours[cluster_num]]
    new_val = tuple(new_val)
    pixelsNew[i, j] = new_val

  return imNew


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

def calculateWeightsForColour(pixels, sz, channel):
  """Calculate weighting for how strong each pixel is in given colour channel (r, g, b)
  This can be supplied to use weighted KMeans clustering which will EMPHASIZE the given channel.
  Takes a 1-D pixel array, returns 1-D array of weights 1 to 10
  """

  #To start, check whether chosen channel represents more than some frac of total brightness, then assign weight of 2

  weights = ones(sz[0]*sz[1]-1)
  channels = ['r', 'g', 'b']
  if(channel not in channels): return weights

  channel_num = channels.index(channel)

  for n in range(0, sz[0]*sz[1]-1):
    val = pixels[n][channel_num]
    bright = 1 + pixels[n][0] + pixels[n][1] + pixels[n][2]
    if(val/bright > 0.5): weights[n] = 10
    #print(weights[n])

  return weights

def calculateWeightsForChannel(pixels, sz, channel):
  """Calculate weighting for how strong each pixel is in given channel ((s)hade, br(i)ght/(i)ntense)
  This can be supplied to use weighted KMeans clustering which will EMPHASIZE the given channel
  Takes a 1-D pixel array, returns 1-D array of weights 1 to 10
  """
  #TODO- implement
  return ones(sz)
