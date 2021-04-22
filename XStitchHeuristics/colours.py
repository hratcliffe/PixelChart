import csv
from math import sqrt

class colourChart:

  def __init__(self, filename='DMCData.csv'):
  
    from importlib_resources import files
    coloursFile = files('Data').joinpath(filename)

    self.chart = []
    with open('Data/DMCData.csv', 'r') as infile:
      rdr=csv.reader(infile, delimiter=',')
      for line in rdr:
        self.chart.append(colourChartItem(name=line[1], num=(line[0]), r=int(line[2]), g=int(line[3]), b=int(line[4]), brand='DMC'))
        
        
    self.searchTree = buildTree(self.chart, index='order', data='rgb') 

  def euclideanDist(colour1, colour2):

    return (sqrt((colour1[0]-colour2[0])**2 + (colour1[1]-colour2[1])**2 + (colour1[2]-colour2[2])**2))

  def matchColour(self, colourIn, numOptions=1, dist=euclideanDist):
    #Return closest colour(s) to given one, using distance algorithm as given
    # Default is to return single closest, numOptions is the number of matches, best to worst, to return
    print("Not implemented yet")
    pass
    
def buildTree(lst, index, data):
  # Build search tree for rapid searches over `list`. index is the property to use as the key, data is the property name to use as the distance. Data should be a triplet
  
  for cnt, item in enumerate(lst):
    if index =='order':
      ind = cnt
    else:
      ind = getattr(item, index)
    print(ind, getattr(item, data))

  print("Not implemented yet")

class colourChartItem:

  def __init__(self, name='Name', num=0, r=0, g=0, b=0, brand="n/a"):
  
    self.name = name
    self.num = num 
    self.brand = brand
    self.rgb = (r, g, b)
    
    
