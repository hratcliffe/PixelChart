from PyQt5.QtWidgets import QDialog, QGridLayout, QPushButton
from PyQt5.QtCore import pyqtSignal

from .colour_comparator import ColourComparator
from ColourHandling.interfaceRoutines import recolour
from SharedData.types import ColourRemapPayload

class RecolourDialog(QDialog):

  image_recoloured = pyqtSignal(ColourRemapPayload, name="image_recoloured")

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
      # Make changes to image
      recolour(image, selections)
      # Emit details of changes
      self.image_recoloured.emit(ColourRemapPayload(self.palette, selections))
      
    