#! /usr/bin/env python3

# Arguments - #1 Filename/path

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

  im = imageExt.imageFromFile(filename)

  # Merge colours to limit to 50 max
  reduceColours(im, 50)

  # Get Symbolic Image
  im_symb = toSymbolicImage(im)

  # Create key as list
  key = getKey(im)

  meta ={'image':im, 'symbolic':im_symb, 'key': key}

  return meta

if __name__ == "__main__":

  # If run from command line, drop 0th arg (script name)
  args = argv[1:]

  allD = main(args)

  allD['image'].show()

