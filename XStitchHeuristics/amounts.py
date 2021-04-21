from math import sqrt

from ColourHandling import imageExt

_perStitch = None  # Approx m per stitch thread for common gauges
_rowFactor = 0.1 # Factor extra for continuous rows
_scatterFactor = 0.3 # Factor extra for scattered elements

_gauges = [14, 16, 18, 20]


def getGauges():
  global _gauges
  return _gauges
  
def calcPerStitch():
  # Calc in m
  global _gauges, _perStitch
  if _perStitch is None:
    _perStitch = {}
    for g in _gauges:
      #{14:0.01, 16:0.008, 18:0.007, 20:0.006}   
      stSize = 2.0 + 2.0*sqrt(2)  # Size of a stitch minimum in terms of edge size
      edgeSize = 2.54e-2/g # Edge size in m
      _perStitch[g] = edgeSize*stSize * 1.1 # Add 10% for angles, tension etc
      

def estimateLength(image, colour, gauge):
  """Estimate thread required for a given image and colour, at specified gauge"""
  global _perStitch, _rowFactor, _scatterFactor

  calcPerStitch()

  l = 0
  l = _perStitch[gauge] * image.colourCounts[colour]

  # Approx fraction that is rows, and that is scatter
  # For scatter, take as rows less than 4 stitches wide (1, 2 or 3)
  num_st_in_rows = 0
  for row in image.runImage:
    for item in row:
      if item[0] == colour:
        if item[1] > 3:
          num_st_in_rows = num_st_in_rows + item[1]
  row_frac = num_st_in_rows/image.colourCounts[colour]
  scatt_frac = 1 - row_frac        
  print(row_frac, scatt_frac)
  return l * 1+(row_frac*_rowFactor + scatt_frac*_scatterFactor)


def estimateSize(imageSz, gauge):

  """Calculate size based on given gauge. Sz should be pair, width then height. Return is
  dict with cm and in sizes"""

  cmPerInch = 2.54
  sz = {}
  sz['in'] = (imageSz[0]/gauge, imageSz[1]/gauge)
  sz['cm'] = (cmPerInch * imageSz[0]/gauge, cmPerInch *imageSz[1]/gauge)

  return sz
