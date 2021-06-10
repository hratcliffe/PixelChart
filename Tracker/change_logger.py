from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from SharedData.types import *

import json

# Custom JSON serialization from https://stackoverflow.com/questions/18478287/making-object-json-serializable-with-regular-encoder/18561055#18561055

def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)

_default.default = json.JSONEncoder.default  # Save unmodified default.
json.JSONEncoder.default = _default # Replace it.


#QT aware change logger wrapper
class ChangeLoggerQt(QObject):

  def __init__(self):
    super(ChangeLoggerQt, self).__init__()
    self.coreLogger = ChangeLogger()


  #@pyqtSlot(XPayload)  #How decorate for multiple possible arg types?
  def store(self, change):
    self.coreLogger.store(change)

  def write(self, filename):
    self.coreLogger.write(filename)  

  def start(self):
    self.coreLogger.start()

  def pause(self):
    self.coreLogger.pause()

  def reset(self):
    self.coreLogger.reset()

  def debug_dump(self):
    self.coreLogger.debug_dump()


#Internal change logger 
class ChangeLogger:

  def __init__(self):
    self.changeList = []
    self.track = False
    
  def store(self, change):
    #Expects one of the Payload Types from SharedData - only needs __repr__ method tho'
    if self.track:
      self.changeList.append(change)
    
  def write(self, filename):
     with open(filename, 'w') as outfile:
      json.dump(self.changeList, outfile)
      
  def start(self):
    self.track = True

  def pause(self):
    self.track = False

  def reset(self):
    self.track = False
    self.changeList = []

  def debug_dump(self):
    for item in self.changeList:
      print(str(item))