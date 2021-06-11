from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from SharedData.types import *
from GUI.image_display import ImageHandler

import json

#Loads a macro set and invokes runner on result
class MacroLoader:

  def __init__(self, runner=None):
    
    if runner:
      self.runner = runner
    else:
      # Default runner
      self.runner = MacroRunnerQt()
  
  def run(self, items):
    self.runner.run(items)

  def run_file(self, filename, showProgress=False):
  
    with open(filename, 'r') as infile:
      items = json.load(infile)
    self.runner.run(items)

  def get_names(self, filename):
    # Attempt to extract LAST values for input and output filenames
    # Our JSON is a list, so order IS guaranteed
    with open(filename, 'r') as infile:
      items = json.load(infile)
    
    for item in items[::-1]:
      if item['name'] == 'PatternPayload':
        break
    for item2 in items[::-1]:
      if item2['name'] == 'ImageLoadPayload':
        break
    try:
      f2 = item2['filename']
    except:
      f2 = ""
    try:
      f1 = item['filename']
    except:
      f1 = ""
    
    return (f2, f1)

  def set_pattern_name(self, filename):
    # Set over-riding pattern file-name, which will be used instead of value from macros file    
    self.runner.set_filename('pattern', filename)

  def set_input_name(self, filename):
    # Set over-riding input file-name, which will be used instead of value from macros file    
    self.runner.set_filename('input', filename)



#Any saveable macro item needs corresponding signal in this class
# Macro Runner needs to have suitable signals (for any runnable macro item) and also implement run method for list of items. It should also support over-riding filenames for input and patterns via set_filename(self, type, filename) method and store/use this
class MacroRunnerQt(QObject):

  image_changed = pyqtSignal(ImageStatePayload, name="image_changed")
  image_change_request = pyqtSignal(ImageChangePayload, name="image_change_request")
  image_resize_request = pyqtSignal(ImageSizePayload, name="image_resize_request")
  pattern_save_request = pyqtSignal(PatternPayload, name="pattern_save_request")

  def __init__(self):
    super(MacroRunnerQt, self).__init__() 
    self.pattern_file = None
    self.input_file = None

  def set_filename(self, type, filename):
  
    if type == "pattern":
      self.pattern_file = filename
    elif type == "input":
      self.input_file = filename

  def run(self, items):
  
    #If-else chain to identify which known operation we have, construct the appropriate Payload and invoke the appropriate signal. This way we can restrict to a specific set of objects that can be created

    for item in items:
      try:
        if(item['name'] == "ImageStatePayload"):
          payload = ImageStatePayload(item['sz'], item['n_cols'])
          self.image_changed.emit(payload)
        elif(item['name'] == "ImageChangePayload"):
          payload = ImageChangePayload(item['n_cols'], item['opts'])          
          self.image_change_request.emit(payload)
        elif(item['name'] == "PatternPayload"):
          if self.pattern_file:
            filename = self.pattern_file
          else:
            filename = item['filename']
          payload = PatternPayload(filename, item['details'])
          self.pattern_save_request.emit(payload)
        elif(item['name'] == "ImageSizePayload"):
          payload = ImageSizePayload(item['width'], item['height'])
          self.image_resize_request.emit(payload)
        elif(item['name'] == "ColourRemapPayload"):
          # TODO what is sensible way to handle this? What would somebody want it to do?
          payload = ColourRemapPayload(item['brand'], item['remap'])
      except:
        # TODO better error here
        print("Error running macro step {}".format(item))
        return
