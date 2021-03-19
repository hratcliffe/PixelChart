#! /usr/bin/env python3

# Arguments - #1 Filename/path
#   All subsequent args are optional
#			- #2 scale - Upscaling factor (integer). Default is 10
#			- #3 guides - Guide locations (in original pixels). To get NO guides, specify an empty list ()
#			- #4 style - Style ('d'ot, 'l'ine, 'p'lus, 'n'one, 'c'ontrast) for ALL guides (or specify per guide, below). Dot is a single pixel dot at each corner, Line is a full outline of each pixel, Plus is a + sign at each corner (3 new pixels wide), None is nothing - use if you don't want each pixel guided. Contrast is as plus, but centre pixel is inverted colour. Default is Dot

#			- #5 colour - Custom colour - RGB triplet. Use to give custom colour for ALL guide marks. Default is black.
#                 - IF image has an alpha channel, can supply an RGBA quadruplet instead - opacity will be ignored if not available in image and will be added as opaque if required and not supplied
#			- #6 g_styles - Guide styles - list of length n_guides of style codes. Note these will be added in order, so if 2 guide specs appear at the same location, the symbols will be printed one above the other. If this is not given, all guide styles will match the global style
# Output file will be input name with "_chart" infixed.


#E.g. ./PixelArtToPattern.py "Squirrel.png", scale=10, style=d, guides=(1)
# OR ./PixelArtToPattern.py "Squirrel.png", scale=10, guides =(5, 10, 20), g_styles=(d, p, l)


from PIL import Image
from sys import argv

from ColourHandling import *

def print_use():
  """Print usage information"""
  print("Please supply filename first and remaining arguments with '=', e.g. `style=d`")


def split_args(args):
  """ Process args assuming a=b formatting """
  new_args = {}
  for item in args:
    segs=item.split('=')
    if(len(segs) == 2):
      new_args[segs[0].strip()] = segs[1].strip()
    else:
      print_use()
  return new_args


def add_guide(image, sz, spacing, style, colour):
  """ Add a SINGLE set of guide lines with defined spacing, style and colour
      E.g. adds lines at 0, spacing, spacing*2, spacing*3...
      Image should be accessible with [], sz should be 2-tuple of dimensions
      For instance, results of PIL.Image.load() and PIL.Image.size
      Style is a single character specified in description above
      Colour is value pixels should be given, e.g. an RGB or RGBA tuple for PIL Images
      NB for 'c'ontrast style, range is assumed to be (0,255)"""

  # Guide style None - do nothing
  if(style == 'n'):
    return

  # Guides placed at multiples of spacing
  for i in range(0, sz[0], spacing):
    for j in range(0, sz[1], spacing):

      # Set central pixel
      image[i,j] = colour
      # Also set additional pixels
      if(style == 'l'):
        line = int(spacing/2)
      elif (style == 'p' or style == 'c'):
        line = int(spacing/4)
      if(style != 'd'):
        for ii in range(-line, line+1):
          try:
            image[i+ii, j] = colour
            image[i, j+ii] = colour
          except:
            pass
      # For contrast style, central pixel is contrasting colour
      if(style == 'c'):
        rev_colour = ()
        for k in range(3):
          rev_colour = rev_colour + ( 255-colour[k],)
        for k in range(3, len(colour)):
          rev_colour = rev_colour + (colour[k],)
        image[i, j] = rev_colour

def main(args):

  # Must have at least one argument - the filename
  if(len(args) < 1):
    print_use()
    print("Nothing Done")
    return

  # Get filename, and parse all other args
  filename = args[0]
  other_args = split_args(args[1:])

  # Scaling factor is an integer
  try:
    scale = int(other_args['scale'])
  except:
    scale = 10

  # Style should be a single character
  try:
    style = other_args['style']
  except:
    style = 'd'

  # List of comma-sep guide positions
  try:
    guides_els = other_args['guides'].strip('()').split(',')
    guides = [int(el) for el in guides_els]
  except:
    guides = []

  try:
    g_styles= other_args['g_styles'].strip('()').split(',')
  except:
    g_styles = []

  try:
    colour = other_args['colour'].strip('()').split(',')
    colour = (int(colour[0].strip(' ')), int(colour[1].strip(' ')), int(colour[2].strip(' ')))
  except:
    colour = (0,0,0)

  # Re-do defaults if guides was not supplied - for this we do basic most useful option, and
  # Overwrite specified styles
  if 'guides' not in other_args:
    guides = [1, 10]
    g_styles = ['d', 'l']


  #Open image
  try:
    im = Image.open(filename)
  except:
    print("File not found or could not be opened. Please try again! Sorry!")
    return

  if im.mode == 'RGB':
    colour_len = 3
  elif im.mode == 'RGBA':
    colour_len = 4
  else:
    # DOn't know what to do - try assuming user knows required shape
    colour_len = len(colour)

  # Add opacity to colour, IF REQUIRED only, and trim if over length
  if len(colour) > colour_len:
    colour = colour[0:colour_len]
  if im.mode == 'RGBA' and len(colour) == 3:
    colour = colour + (255,)

  # Parse guides - add style and colour info to make (spacing, style, colour) tuple
  full_guides = []
  if len(g_styles) == len(guides):
    for i in range(len(guides)):
      full_guides.append([guides[i], g_styles[i], colour])
  else:
    for guide in guides:
      full_guides.append([guide, style, colour])

  #Upscale image by scale factor
  sz = im.size
  new_sz = [ el * scale for el in sz]
  im_big = im.resize(new_sz, Image.BOX)

  # Get pixel map to modify
  pixels = im_big.load()
  # Add all guides
  for guide in full_guides:
    add_guide(pixels, im_big.size, guide[0]*scale, guide[1], guide[2])

  # Infix '_chart' to file name just before extension and save image
  ofile = filename.split('.')
  ofile[-2] = ofile[-2] + "_chart"
  ofile= '.'.join(ofile)

  im_big.save(ofile)

if __name__ == "__main__":

  # If run from command line, drop 0th arg (script name)
  args = argv[1:]

  main(args)

