from PyQt6.QtWidgets import QDialog, QGridLayout, QPushButton, QVBoxLayout, QScrollArea
from PyQt6.QtCore import pyqtSignal

from .colour_comparator import ColourComparator
from .colour_combiner import ColourPicker
from ColourHandling.interfaceRoutines import recolour, recolourFromList
from ColourHandling.colourDistances import *
from SharedData.types import ColourRemapPayload

class RecolourDialog(QDialog):
  """Dialog dealing with mapping image colours to a specific colour palette.
  Mostly hosts a comparator widget to show colours one at a time, along with closest palette options
  Each colour can be remapped or skipped and entire process can be aborted.
  """

  image_recoloured = pyqtSignal(ColourRemapPayload, name="image_recoloured")

  def __init__(self, palette):
    super(RecolourDialog, self).__init__()

    # Palette is required to provide colour matches
    self.palette = palette
    if self.palette is None:
      return

    # Picker widget
    self.pickerWidget = ColourComparator(chart=palette)
    self.layout = QGridLayout()
    self.layout.addWidget(self.pickerWidget, 0, 0)

    # Button controls
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
    """ Show colours in image one by one along with closest palette matches and
    capture user selections for remap.
    If process is cancelled, do nothing, otherwise trigger recolouring of image
    """
    if self.palette is None:
      return

    cancel = False

    self.contin = False
    # Run pickers and compile list of selections
    selections = {}
    for colour in image.colourMap[0].keys():
      self.pickerWidget.show_colour(colour)
      res = self.exec() # Call once per colour and grab selection each time
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

#TODO: hook this to the tracker!!
class CombinerDialog(QDialog):
  """ Dialog dealing with merging multiple colours together. Mostly hosts
    a ColourPicker widget, plus button controls.
    On creation, should be passed a callback function to be executed if a
    colour merge is requested
  """

  def __init__(self, image, callback):
    super(CombinerDialog, self).__init__()

    # Sort colour list into some sort of order. For user ease we want similar colours to be close
    # together, as these are likely to be the ones one wants to merge
    self._colours = sorted(image.getColours(), key = lambda c: calculateDistanceRef(c)) # ToDO - colour value-y sort?

    self.setWindowTitle("Select a colour to combine:")

    # Picker widget
    self.pickerWidget = ColourPicker(self._colours, callback)
    self.layout = QGridLayout()

    self.scroller = QScrollArea()
    self.layout.addWidget(self.scroller, 0,0)
    self.scroller.setWidget(self.pickerWidget)
    self.scroller.setWidgetResizable(True)

    # Button controls
    self.done_butt = QPushButton()
    self.done_butt.setText("Done")
    self.layout.addWidget(self.done_butt, 1,1)

    self.setLayout(self.layout)

    self.done_butt.clicked.connect(self.is_done)


  def is_done(self):
    self.close()

