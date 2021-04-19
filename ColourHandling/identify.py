from math import sqrt, atan2, pi

def nameColour(colourTriplet, mode = 'RGB'):

  if mode in ['RGB', 'rgb']:
    return nameColourRGB(colourTriplet)
  elif mode in ['lab', "LAB", 'Lab']:
    return nameColourLAB(colourTriplet)
  else:
    return None

def nameColourLAB(colourTriplet):

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
    name.append("cyan")
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

def nameColourRGB(colourTriplet):
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


