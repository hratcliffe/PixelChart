# Experimental feature detection module
from . import imageExt

from sklearn.cluster import KMeans
from skimage import feature
from PIL import ImageOps

import numpy as np
import matplotlib.pyplot as plt
import cv2
  
  
def findFeaturesCanny(imageIn, plot = False, sigma=1.2, doClose=False, channel=None):
  """ Expects a PIL image """

  chn = channel
  if channel in [0, 1, 2, "R", "G", "B", 'r', 'g', 'b']:
    # Use only requested channel
    imProcess = np.asarray(imageIn.getchannel(channel))
  elif channel in [-1, "x", 'X']:
    # Split channels and combine the results of each
    imProcess = imageIn.split()
    chn = -1
  else:
    # Create greyscale version of image as np array
    imProcess = np.asarray(ImageOps.grayscale(imageIn))
      
  
  if chn != -1:
    edges = feature.canny(imProcess, sigma=sigma)  
  else:
    edges = feature.canny(np.asarray(imProcess[0]), sigma=sigma)
    for c in range(2):
      edgesTmp = feature.canny(np.asarray(imProcess[c]), sigma=sigma)
      for i in range(0, imProcess[0].size[1]-1):
        for j in range(0, imProcess[0].size[0]-1):
          edges[i,j] = edges[i,j] + edgesTmp[i,j]
    edges = 255*edges/3
    edges = edges.astype(int)

  if plot:
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(edges, cmap=plt.cm.gray)
    plt.show()
    
  return edges


def closeFeatureLines(imageIn, closureWidth=1):

  """Close lines by dilating and eroding them, with width as given"""

  kernel = np.ones((3, 3), np.uint8)
  
  image = imageIn.astype('uint8') 
  
  dilation_image = cv2.dilate(image, kernel, iterations=1)
  erosion_image = cv2.erode(dilation_image, kernel, iterations=1)

  return erosion_image


def removeFeatureBlobs(imageIn, blobWidth=1):

  """Remove blobs by eroding and dilating then subtracting result from original, with width as given"""

  
  working_image = imageIn.astype('uint8') 

  kernelWidth = blobWidth*2+1
  kernel = np.ones((kernelWidth, kernelWidth), np.uint8)

  erosion_image = cv2.erode(working_image, kernel, iterations=1)
  working_image = cv2.dilate(erosion_image, kernel, iterations=1)

  diff_image = imageIn - working_image

  return diff_image

def removeFeatureBlobsAdaptive(imageIn, blobWidth=1):

  """Remove blobs by killing pixels which are surrounded, and a ring around this"""

  working_image = imageIn.astype('uint8') 

  blob_mask = np.ones((len(imageIn), len(imageIn[0])), np.uint8)

  # Squash all cells with too many surroundings
  for i in range(1, len(imageIn)-1):
    for j in range(1, len(imageIn[0])-1):
    
      neighbours = working_image[i-1, j-1] + working_image[i-1, j] + working_image[i-1, j+1] + working_image[i, j-1] + working_image[i, j+1] + working_image[i+1, j-1] + working_image[i+1, j] + working_image[i+1, j+1]
      
      if neighbours > 7:
        blob_mask[i,j] = 0
  
  kernel = np.ones((3, 3), np.uint8)
  blob_mask = cv2.erode(blob_mask, kernel, iterations=1)

  plt.figure()
  plt.imshow(blob_mask, cmap="gray")
  plt.show()


  diff_image = cv2.bitwise_and(working_image, blob_mask)

  return diff_image

def findColourRegions(imageIn):

  """Find regions by detecting sharp changes in hue. Input should be a PIL image in LAB mode"""
  
  
  

