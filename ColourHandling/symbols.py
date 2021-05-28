from os import linesep

#All symbols are 9x9 pixel elements, since this is a good upscaling size and gives moderate detail levels, while leaving one pixel for edging etc in a 10x10 square
# See txt file for shapes

_symSize = 9
_edgSize = 1

_symbols = None

class SymbolDefinitionError(Exception):
  pass

class Symbol:
  nullSyms = ['0', ' ']
  
  def __init__(self, data, name_in):
    self.locs = self.locsFromData(data)
    self.name = name_in

  def locsFromData(self, data):
    """ Convert from list-of-lists data array into a single list of coordinate locations. Data must be rectangular!"""
    locs = []
    
    # Can either - get unique symbols, verify there are 2, identify which is null
    # OR just check each time for a valid null. These options behave the same for
    # VALID data (one null, one non-null symbol), but differently for partly invalid data

    for i, line in enumerate(data):
      for j, el in enumerate(line):
        if el not in self.nullSyms:
          locs.append((i,j))

    return locs
    
def readSymbols():
  """ Read symbols from txt file, ten lines per, one line before each
  This spare line can be used for a name, it will be completely ignored
  For simplicity, we assume spaces and zero characters are to be background colour, and anything else is foreground
  """
  
  from importlib_resources import files
  symbolsFile = files('ColourHandling').joinpath('symbols.txt')
  
  global _symSize
  symbols = []
  with open(symbolsFile, 'r') as infile:
    lines = infile.readlines()

  # Take blocks of symSize+1, skip first and split into individual chars
  offset = 0
  while True:
    try:
      # One line in between symbols for the titles etc
      dataInit = lines[offset+1: offset+_symSize+1]
      dataProcessed = []
      for item in dataInit:
        itemSyms = [char for char in item if char is not linesep]
        dataProcessed.append(itemSyms)
      symbols.append(Symbol(dataProcessed, lines[offset].strip('\n')))
    
    except IndexError:
      # End of list reached - this is expected, carry on
      break
    except Exception as e:
      # Some sort of problem with symbols file - raise error
      raise SymbolDefinitionError
      break
    offset = offset + _symSize + 1
  return symbols
        
def getUpscaling():
  """ Upscaling needed to accomodate symbols in image"""
  global _symSize, _edgSize
  return _symSize + _edgSize

def loadSymbols(force = False):
  """Loads Symbols from file into global _symbols. Use force=True to reload regardless of whether symbols are already loaded"""
  global _symbols
  
  if force or _symbols is None:
    _symbols = readSymbols()
  
def getSymbol(id):

  loadSymbols()

  n_id = id%len(_symbols)  #Wrap round if out of range
  return _symbols[n_id]
