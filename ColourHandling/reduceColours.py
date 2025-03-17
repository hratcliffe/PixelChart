#Colour reduction functions - to reduce the number of distinct colours in an image
from .replace import *

from .colourDistances import calculateDistance
from .identify import *

from sklearn.cluster import KMeans
from PIL import Image
from math import floor, sqrt

from numpy import ones, sinh, concatenate, append

def mergeColours(imageIn, n_cols=20, emph=None, mode='RGB'):
  """Reduce number of colours by clustering. The result will contain exactly n_cols colours. Running this with a large number of end colours is a good first pass at converting a picture into a chart, prior to detailled colour replacements"""

  #If emph is given, upweights the given choice. HOWEVER this does not really change the number of clusters

  # Temporary image as 1-d array of colours
  data = imageIn.getdata()
  sz = imageIn.size

  if emph:
    if emph in ['r', 'g', 'b']:
      weights = calculateWeightsForColour(data, sz, emph, mode=mode)
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

def mergeColoursEmphasized(imageIn, n_cols=20, emph=None, mode='RGB'):
  """Reduce number of colours by clustering. The result will contain exactly n_cols colours. Running this with a large number of end colours is a good first pass at converting a picture into a chart, prior to detailled colour replacements"""

  #If emph is given, splits the pixels into two lists and puts 50% more clusters into the selection than come out on a first pass
  # NOTE: this does run clustering 3 times as opposed to 1

  #Emph not present or not known
  if not emph or (emph not in ['r', 'g', 'b', 's', 'i']):
    return mergeColours(imageIn, n_cols)

  # Temporary image as 1-d array of colours
  data = imageIn.getdata()
  sz = imageIn.size


  # Round one: plain clustering
  # Only do this once because we just want to know how many 'emph'-ish clusters there are
  kmeans = KMeans(n_clusters=n_cols, n_init=1, random_state=42)
  kmeans.fit(data)

  # Find out how many clusters went into the 'emph' phase-space-region
  n_in = 0
  inClusters = []
  inClustersInd = []
  for i in range(len(kmeans.cluster_centers_)):
  #for item in kmeans.cluster_centers_ :
    item = kmeans.cluster_centers_[i]
    if emph in ['r', 'g', 'b']:
      if mode == 'RGB':
        isIn = isPrimaryRGB(item, emph)
      elif mode == 'LAB':
        isIn = isPrimaryLAB(item, emph)
    else:
      isIn = False # TODO fix this
    if isIn:
      n_in += 1
      inClustersInd.append(i)
      inClusters.append(item)

  recut = False

  # Assign 50% over (up to 90% of all unless already over 90%)
  #TODO Use a sinh roll-off between?
  if n_in == 0:
    recut = False
  elif n_in * 1.5/n_cols < 0.9:
    t_n_in = floor(n_in * 1.5)
    recut = True
  elif n_in/n_cols < 0.9:
    t_n_in = floor(n_cols * 0.9)
    recut = True

  if recut:
    print("Emphasizing - increasing from {} to {}: ".format(n_in, t_n_in))
  else:
    print("Emphasizing rejected - did not increase cluster number")

  if recut:
    # Now run clustering on the in-group and out-group individually IF recut is true

    in_pix_indices = []
    in_pix_array = []
    out_pix_indices = []
    out_pix_array = []

    #  Select in group pixels and cache indices of them
    for k in range(0, sz[0]*sz[1]-1):
      if kmeans.labels_[k] in inClustersInd:
        in_pix_indices.append(k)
        in_pix_array.append(data[k])
      else:
        out_pix_indices.append(k)
        out_pix_array.append(data[k])

    #  Cluster ingroup
    kmeans_in = KMeans(n_clusters=t_n_in, n_init=3, random_state=42)
    kmeans_in.fit(in_pix_array)
    print("Colour reduction on Emph group complete after {} iterations. Final inertia {}".format(kmeans_in.n_iter_, kmeans_in.inertia_))

    #  Cluster outgroup
    kmeans_out = KMeans(n_clusters=n_cols-t_n_in, n_init=3, random_state=42+7)
    kmeans_out.fit(out_pix_array)
    print("Colour reduction on Others complete after {} iterations. Final inertia {}".format(kmeans_out.n_iter_, kmeans_out.inertia_))


    # Put it all back together
    #  Reconstruct the full list of centres
    #centres = kmeans_in.cluster_centers_
    #for item in kmeans_out.cluster_centers_:
    #  append(centres, item)
    centres = concatenate((kmeans_in.cluster_centers_, kmeans_out.cluster_centers_), axis=0)
    offset = len(kmeans_in.cluster_centers_)
    labels = []
    #  Bump outgroup centre indices - map labels up
    for k in range(0, sz[0]*sz[1]-1):
      if k in in_pix_indices:
        kk = in_pix_indices.index(k)
        labels.append(kmeans_in.labels_[kk])
      else:
        #TODO -trap impossible where pixel is in neither?
        kkk = out_pix_indices.index(k)
        labels.append(kmeans_out.labels_[kkk] + offset)

  else:
    # Fill the names from the original cluster
    # TODO - should we re-run with more randomisations?
    centres = kmeans.cluster_centers_
    labels = kmeans.labels_

  # Create new image where each colour is remapped to the centroid of its cluster.

  new_colours = []
  # Convert from arrays back to tuples
  for item in centres :
    new_colours.append (tuple(item))

  # Create new image with replaced colours. Initialise to 0s
  imNew = Image.new(imageIn.mode, sz, (0,0,0))
  pixelsNew = imNew.load()

  # Remap
  for k in range(0, sz[0]*sz[1]-1):
    j = int(floor(k/sz[0]))
    i = int(k - j * sz[0])
    cluster_num = labels[k]
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

def calculateWeightsForColour(pixels, sz, channel, mode='LAB'):
  """Calculate weighting for how strong each pixel is in given colour channel (r, g, b)
  This can be supplied to use weighted KMeans clustering which will EMPHASIZE the given channel.
  Takes a 1-D pixel array, returns 1-D array of weights 1 to 10
  """

  weights = ones(sz[0]*sz[1]-1)
  channels = ['r', 'g', 'b']
  if(channel not in channels): return weights

  if mode == 'LAB':
    #Triplet is in LAB space. Do r-theta id
    for n in range(0, sz[0]*sz[1]-1):
      val = pixels[n]
      if isPrimaryLAB(val, channel):
        weights[n] = 10
    print(weights)
  else:
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
