from PyQt5.QtWidgets import QDialog, QGridLayout, QPushButton, QVBoxLayout

from .colour_comparator import ColourComparator
from .colour_combiner import ColourPicker
from ColourHandling.interfaceRoutines import recolour, recolourFromList
from ColourHandling.colourDistances import *

class RecolourDialog(QDialog):

  def __init__(self, palette):
    super(RecolourDialog, self).__init__() 
    
    self.palette = palette
    if self.palette is None:
      return

    self.pickerWidget = ColourComparator(chart=palette)
    
    self.layout = QGridLayout()
    self.layout.addWidget(self.pickerWidget, 0, 0)
    
    self.skip_butt = QPushButton()
    self.skip_butt.setText("Skip and Next")
    self.layout.addWidget(self.skip_butt, 1, 1)

    self.next_butt = QPushButton()
    self.next_butt.setText("Accept and Next")
    self.next_butt.setDefault(True)
    self.layout.addWidget(self.next_butt, 1, 2)
        
    self.setLayout(self.layout)

    self.skip_butt.clicked.connect(self.skip)
    self.next_butt.clicked.connect(self.accept)

  def skip(self):
    # This is an ugly hack to allow accept, skip-and-continue, and reject entire process. Check the self.contin property when reject occurs to distinguish
    self.contin = True
    self.close()
    
    
  def do_recolour(self, image):

    if self.palette is None:
      return

    cancel = False
 
    self.contin = False
    # Run pickers and compile list of selections
    selections = {}
    for colour in image.colourMap[0].keys():
      self.pickerWidget.show_colour(colour)
      res = self.exec_() # Call once per colour and grab selection each time
      if res:
        choice = self.pickerWidget.get_selected()
        selections[colour] = choice[1].rgb
      elif self.contin:
        self.contin = False
      else:
        cancel = True
        break # Dialog reject or close cancels entire process

    # If process cancelled, assume do nothing
    if cancel:
      return
    else:
      recolour(image, selections)
    
class CombinerDialog(QDialog):

  def __init__(self, image, callback):
    super(CombinerDialog, self).__init__() 
    
    self._colours = sorted(image.getColours(), key = lambda c: calculateDistanceRef(c)) # ToDO - colour value-y sort?
    self._colourMap = {} #Key: Original colour, Val: List of those to combine
    self._image = image

    self.pickerWidget = ColourPicker(self._colours, callback)
    
    self.layout = QGridLayout()
    self.layout.addWidget(self.pickerWidget, 0,0)
    
    self.done_butt = QPushButton()
    self.done_butt.setText("Done")
    self.layout.addWidget(self.done_butt, 1,1)
        
    self.setLayout(self.layout)

    self.done_butt.clicked.connect(self.is_done)


  def is_done(self):
    self.close()
    




