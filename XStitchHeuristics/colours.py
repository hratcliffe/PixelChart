import csv

from General.searcher import *

def listBrands():

  from importlib_resources import files
  brandsFile = files('Data').joinpath('brands.csv')
  with open(brandsFile, 'r') as infile:
    rdr = csv.reader(infile, delimiter=',')
    lines = list(rdr)

  return(lines)

class colourChart:

  def __init__(self, brand = "DMC"):
  
    from importlib_resources import files
    filename = brand + '_Data.csv'

    # Check brand is valid and get short-code
    brandsFile = files('Data').joinpath('brands.csv')

    gotBrand = False
    with open(brandsFile, 'r') as infile:
      rdr = csv.reader(infile, delimiter=',')
      for line in rdr:
        if brand in line:
          gotBrand = True
          self.brandCode = line[1]

    if not gotBrand:
      print("Error - no colour data for {}".format(brand))
      return

    coloursFile = files('Data').joinpath(filename)

    self.isCustom = "Custom" in brand

    self.brand = brand  # Brand can also be special value "Custom" which implies a mixture - each colour can differ - otherwise each colour can either be as parent, or be Brand None
    self.srcfile = filename

    self.chart = []
    with open(coloursFile, 'r') as infile:
      rdr = csv.reader(infile, delimiter=',')
      if self.isCustom:
        for line in rdr:
          self.chart.append(colourChartItem(name=line[1], num=(line[0]), r=int(line[2]), g=int(line[3]), b=int(line[4]), brand=line[5]))
      else:
        for line in rdr:
          self.chart.append(colourChartItem(name=line[1], num=(line[0]), r=int(line[2]), g=int(line[3]), b=int(line[4]), brand=brand))
        
    self.searcher = buildTreeProperty(self.chart, data='rgb') 

  def matchColour(self, colour, numOptions=1):
    #Return closest item to given one
    # Default is to return single closest, numOptions is the number of matches, best to worst, to return
    return self.searcher.find(colour, numOptions)

class colourChartItem:

  def __init__(self, name='Name', num=0, r=0, g=0, b=0, brand=None):
  
    self.name = name
    self.num = num 
    self.brand = brand
    self.rgb = (r, g, b)
    
  def __str__(self):
    return "{}, {}, ({})".format(self.num, self.name, self.rgb)

class colourItem:

  def __init__(self, r=0, g=0, b=0):
  
    self.rgb = (r, g, b)
    
  def __str__(self):
    return "({})".format(self.rgb)
