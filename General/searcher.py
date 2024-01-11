import numpy as np
from math import sqrt
from scipy.spatial import KDTree


def buildTreeProperty(lst, data):
  # Build search tree for rapid searches over `list`. data is the property name to use as the distance. Data should be a triplet

  dat_arr = np.zeros((len(lst), 3))
  for cnt, item in enumerate(lst):
    dat_arr[cnt] = getattr(item, data)

  sTree = KDTree(dat_arr)
  return searcher(sTree, lst, data)

def buildTreeDirect(lst):
  # Build search tree for rapid searches over `list`. Assumes items in list are triplets

  sTree = KDTree(lst)
  return searcher(sTree, lst, '')

# TODO shouldn't the above be init options for searcher object??
class searcher:
  """Class implementing search on prebuilt KDTree"""
  def __init__(self, tree, items, dataProp):
    self.tree = tree
    self.items = items
    self.dataProp = dataProp
    
  def find(self, item, numOptions):
    #Return closest item to given one
    # Default is to return single closest, numOptions is the number of matches, best to worst, to return

    if self.dataProp != '':
      dist,points = self.tree.query(getattr(item, self.dataProp), numOptions)
    else:
      dist, points = self.tree.query(item, numOptions)

    if numOptions > 1:
      fnd_items = []
      for pt in points:
        fnd_items.append(self.items[pt])
      return fnd_items
    else:
      return self.items[points]
