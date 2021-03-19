
from sklearn.cluster import KMeans
from PIL import Image
from math import floor

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
  
  
def mergeColours(pixels, sz, n_cols=20):
  """Reduce number of colours by clustering. The result will contain at most n_cols colours. Running this with a large number of end colours is a good first pass at converting a picture into a chart, prior to detailled colour replacements"""
  
  # Temporary image as 1-d array of colours
  
  data = []
  for i in range(sz[0]):
    for j in range(sz[1]):
      data.append(pixels[i,j])
      
 
  # Runs a __single__ initialisation trial with requested number of clusters 
  # This might work OK for an image, but might be better turned up
  kmeans = KMeans(init="random", n_clusters=n_cols, n_init=1, max_iter=300,random_state=42)  
  
  kmeans.fit(data)
  
  # Create new image where each colour is remapped to the centroid of its cluster. NB we could skip this and go straight to indexing by cluster number... TODO do something about that?
  
  # TODO can we just do the clustering on the colour list instead? Is it very slow to do replacements?
  
  new_colours = []
  # Convert from arrays back to tuples
  for item in kmeans.cluster_centers_ :
    new_colours.append (tuple(item))

  # Create new image with replaced colours. Initialise to 0s
  imNew = Image.new('RGB', sz, (0,0,0))
  pixelsNew = imNew.load()

  
  # Remap
  for k in range(sz[0]*sz[1]):
    # TODO check this logic is right way round for non-squre
    j = int(floor(k/sz[1]))
    i = int(k - j * sz[1])
    cluster_num = kmeans.labels_[k]
    new_val = [int(c) for c in new_colours[cluster_num]]
    new_val = tuple(new_val)

    #TODO is this transposing input image?
    pixelsNew[i,j] = new_val

  return imNew
  
  
  
  
  

