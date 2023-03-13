from math import sqrt

def calculateDistanceRef(colour):
  """Calculate distance between given colour and reference value"""
  ref = (0, 0, 0)
  return calculateDistance(colour, ref)

def calculateDistance(colour1, colour2):
  """Calculate distance between given colour triplets"""
  return sqrt( (colour1[0]-colour2[0])^2 + (colour1[1]-colour2[1])^2 + (colour1[2]-colour2[2])^2)