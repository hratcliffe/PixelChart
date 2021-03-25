

def nameColour(colourTriplet, mode = 'RGB'):

  if mode in ['RGB', 'rgb']:
    return nameColourRGB(colourTriplet)
  elif mode in ['lab', "LAB", 'Lab']:
    return nameColourLab(colourTriplet)
  else:
    return None


def nameColourRGB(colourTriplet):
  """ Really dumb colour naming. Find channel dominance and darkness """
  
  # Neutrals
  rg = colourTriplet[0] - colourTriplet[1]
  rb = colourTriplet[0] - colourTriplet[2]
  gb = colourTriplet[1] - colourTriplet[2]
  diffs = (rg, rb, gb)
  bright = sum(colourTriplet)
 
  name = ""
 
  # Balanced channels 
  bal = 40
  if abs(rg) < bal and abs(rb) < bal and abs(gb) < bal:
    # Some sort of grey
    
    if bright > 700:
      return "white"
    elif bright > 200:
      return "grey"
    else:
      return "black"

  # Dark or light modifier
  if bright > 600:
    name = "light "
  elif bright < 300:
    name = "dark "
  
  dom = 0.6 * bright
  bal = 40
  # One channel dominance
  if rg > bal or rb > bal or colourTriplet[0] > dom:
    # Red is "most" of brightness
    name += "red"
    return name
  elif -rg > bal or gb > bal or colourTriplet[1] > dom:
    # Green is "most" of brightness
    name += "green"
    return name
  elif -rb > bal or -gb > bal or colourTriplet[2] > dom:
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
    
  