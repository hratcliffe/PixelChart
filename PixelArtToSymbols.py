#! /usr/bin/env python3

# Arguments - #1 Filename/path


from PIL import Image
from sys import argv

from ColourHandling import *

def print_use():
  """Print usage information"""
  print("Please supply filename!")

def main(args):

  # Must have at least one argument - the filename
  if(len(args) < 1):
    print_use()
    print("Nothing Done")
    return

  # Get filename, and parse all other args
  filename = args[0]

  #Open image
  try:
    im = Image.open(filename)
  except:
    print("File not found or could not be opened. Please try again! Sorry!")
    return

  # For simplicity, don't use paletted image
  if im.mode == 'P':
    im = im.convert('RGB')

  if im.mode == 'RGB':
    colour_len = 3
    baseColour = (255, 255, 255)
    lineColour = (0, 0, 0)
  elif im.mode == 'RGBA':
    colour_len = 4
    baseColour = (255, 255, 255, 255)
    lineColour = (0, 0, 0, 255)
  else:
    colour_len = 3
    baseColour = (255, 255, 255)
    lineColour = (0, 0, 0)

  # Get pixel map to modify
  pixels = im.load()
  sz = im.size
  # Identify number of distinct colours and create two way dicts to Ids

  colours = findColours(pixels, sz)
  fw_map, bk_map = mapColours(colours)

  # Limit to max of 50 colours TODO try and reduce by merging?

  # Create new image with each colour replaced with its own symbol
  im_sym = replaceColours(im, fw_map, baseColour, lineColour)
  

  # Create key. TODO add heuristic colour names?


  # TODO estimate thread required



  # Infix '_symbolic' to file name just before extension and save image
  ofile = filename.split('.')
  ofile[-2] = ofile[-2] + "_symbolic"
  ofile= '.'.join(ofile)

  im_sym.save(ofile)

if __name__ == "__main__":

  # If run from command line, drop 0th arg (script name)
  args = argv[1:]

  main(args)

