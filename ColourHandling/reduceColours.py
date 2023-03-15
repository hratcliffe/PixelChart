from .replace import *

from .colourDistances import calculateDistance

from sklearn.cluster import KMeans
from PIL import Image


def mergeColours(imageIn, n_cols=20):
  """Reduce number of colours by clustering. The result will contain exactly n_cols colours. Running this with a large number of end colours is a good first pass at converting a picture into a chart, prior to detailled colour replacements"""
  
  # Temporary image as 1-d array of colours
  data = imageIn.getdata()
  sz = imageIn.size
 
  # Generate n_cols clusters using 5 random initialisations
  kmeans = KMeans(n_clusters=n_cols, n_init=5, random_state=42)  
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