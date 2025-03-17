# Module dealing with naming colours
from math import sqrt, atan2, pi

def nameColour(colourTriplet, mode = 'RGB'):
  """Attempt to give meaningful name to a given colour triplet
  NOTE: This works a LOT better in LAB space than RGB """

  if mode in ['RGB', 'rgb']:
    return nameColourRGB(colourTriplet)
  elif mode in ['lab', "LAB", 'Lab']:
    return nameColourLAB(colourTriplet)
  else:
    return None

def nameColourLAB(colourTriplet):
  """ Attempt to name a colour triplet assuming it is in LAB space
  Combines a measure of the lightness with a position on colour wheel
  Adds Brown and Pink as well as white-grey-black manually
  """

  l, a, b = colourTriplet
  # a- red-green. b- blue-yellow

  r = sqrt((a-128)**2 + (b-128)**2)
  theta = atan2((128-b),(a-128)) + pi

  #Handle central balanced region specially
  if r < 10:
    # Generally balanced greys
    if l > 220:
      return ["","white"]
    elif l > 180:
      return ["l.", "grey"]
    elif l > 120:
      return ["","grey"]
    elif l > 50:
      return ["d.","grey"]
    else:
      return ["","black"]

  if l > 220:
    name = ["vl."]
  elif l > 180:
    name = ["l."]
  elif l > 120:
    name = [""]
  elif l > 50:
    name = ["d."]
  else:
    name = ["vd."]

  # Work in 8 regions of angle, with tweaks to bounds

  #print(a, b, r, theta, pi/8, 3*pi/8)
  if theta > 0 and theta < 3*pi/16:
    name.append("green")
  elif theta < 7*pi/16:
    name.append("lime")
  elif theta < 10*pi/16:
    name.append("yellow")
  elif theta < 12*pi/16:
    name.append("orange")
  elif theta < 17*pi/16:
    name.append("red")
  elif theta < 21*pi/16:
    name.append("purple")
  elif theta < 27*pi/16:
    name.append("blue")
  elif theta < 29*pi/8:
    name.append("cyan")  #TODO is '8' a typo?
  else:
    name.append("green")

  # Amend a few special names

  if name[0] == "d." and (name[1] == "orange" or name[1] == "yellow"):
    name = ["","brown"]
  elif name[0] == "vd." and (name[1] == "orange" or name[1] == "yellow"):
    name = ["d.","brown"]
  elif name[0] == "l." and (name[1] == "orange" or name[1] == "red"):
    name = ["","pink"]
  elif name[0] == "vl." and (name[1] == "orange" or name[1] == "red"):
    name = ["l.","pink"]

  # Amend brightnesses for those removed
  if "yellow" in name or "orange" in name:
    if name[0] == "":
      name[0] = "d."
    elif name[0] == "l.":
      name[0] = ""
    elif name[0] == "vl.":
      name[0] = "l."

  return name

def isPrimaryLAB(colourTriplet, pick):
  """ Return true or false for whether the given triplet 'is' the given primary colour"""
  if pick not in ['r', 'g', 'b']: return False

  l, a, b = colourTriplet
  # a- red-green. b- blue-yellow

  #Very dark or very light are NO colour
  if l < 40 or l > 230: return False

  r = sqrt((a-128)**2 + (b-128)**2)
  theta = atan2((128-b),(a-128)) + pi


  #Central a-b region is not coloured
  if r < 20: return False

  #TODO refine the boundaries

  if theta > 0 and theta < 9*pi/16:
    # Green-ish
    if pick == 'g': return True
  elif theta > 10*pi/16 and theta < 18*pi/16:
    # Red-ish
    if pick == 'r': return True
  elif theta > 19*pi/16 and theta < 29*pi/16:
    # Blue-ish
    if pick == 'b': return True

  return False

def isPrimaryRGB(colourTriplet, pick):
  """ Return true or false for whether the given triplet 'is' the given primary colour"""
  if pick not in ['r', 'g', 'b']: return False

  return isPrimaryLAB(RGB2LAB(colourTriplet), pick)


def nameColourRGB(colourTriplet):
  """Attempt to name colours in RGB space. THIS DOES NOT WORK WELL. If possible
  convert to LAB space and use that """
  # Bad heuristic colour naming. Use LAB if possible!

  # Identify dominances
  rg = colourTriplet[0] - colourTriplet[1]
  rb = colourTriplet[0] - colourTriplet[2]
  gb = colourTriplet[1] - colourTriplet[2]
  diffs = (rg, rb, gb)
  bright = sum(colourTriplet)

  name = ""

  # Balanced channels - divide black/white/grey from brightnesses
  bal = 40
  if abs(rg) < bal and abs(rb) < bal and abs(gb) < bal:
    # Some sort of grey
    if bright > 750:
      return "white"
    elif bright > 500:
      return "light grey"
    elif bright > 300:
      return "grey"
    elif bright > 100:
      return "dark grey"
    else:
      return "black"

  # Dark or light modifier
  if bright > 600:
    name = "light "
  elif bright < 300:
    name = "dark "

  dom = 0.75 * bright
  bal = 40
  # One channel dominance
  if (rg > bal and rb > bal) or colourTriplet[0] > dom:
    # Red is "most" of brightness
    name += "red"
    return name
  elif (-rg > bal and gb > bal) or colourTriplet[1] > dom:
    # Green is "most" of brightness
    name += "green"
    return name
  elif (-rb > bal and -gb > bal) or colourTriplet[2] > dom:
    # Blue is "most" of brightness
    name += "blue"
    return name

  # 2 channel dominance (one channel antidominant)
  antidom = 1.0/4.0 * bright
  bal = bright / 5.0

  if colourTriplet[2] < antidom:
    if rg > bal:
      if bright < 300:
        name += "brown"
        return name
      else:
        name += "orange"
        return name
    else:
      name += "yellow"
      return name
  elif colourTriplet[1] < antidom:
    if rb > bal:
      name += "pink"
      return name
    else:
      name += "purple"
      return name
  elif colourTriplet[0] < antidom:
    name += "blue green"
    return name

  return None

def RGB2LAB(colourTriplet):
  # Formulae from https://www.easyrgb.com/en/math.php
  # Using Daylight illumination

  r, g, b = colourTriplet
  r /= 255
  g /= 255
  b /= 255

  # To intermediate

  if r > 0.04045:
    s = ((r + 0.055)/1.055)**2.4
  else:
    s = r/12.92
  if g > 0.04045:
    t = ((g + 0.055)/1.055)**2.4
  else:
    t = g/12.92
  if b > 0.04045:
    u = ((b + 0.055)/1.055)**2.4
  else:
    u = b/12.92

  s *= 100
  t *= 100
  u *= 100

  x = s * 0.4124 + t * 0.3576 + u * 0.1805
  y = s * 0.2126 + t * 0.7152 + u * 0.0722
  z = s * 0.0193 + t * 0.1192 + u * 0.9505

  D = [95.047, 100.0, 108.883]
  x /= D[0]
  y /= D[1]
  z /= D[2]

  if x > 0.008856:
    x = x**0.333
  else:
    x = (7.787 * x ) + 16/116
  if y > 0.008856:
    y = y**0.333
  else:
    y = (7.787 * x ) + 16/116
  if z > 0.008856:
    z = z**0.333
  else:
    z = (7.787 * z ) + 16/116

  l = (116 * y) - 16
  a = 500 * (x - y)
  b = 200 * (y - z)

  #Using Pillow where all run 0 to 255
  l *= 255/100
  a += 128
  b += 128

  return (l, a, b)
