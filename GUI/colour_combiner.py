from PyQt6.QtWidgets import QDialog, QWidget, QLabel, QPushButton, QGridLayout, QCheckBox
from PyQt6.uic import loadUi
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import QVariant

from ColourHandling.interfaceRoutines import makeSwatch
from General.searcher import *
from .types import ImageCombinePayload


from importlib_resources import files
from PIL.ImageQt import toqpixmap
from re import match as re_match

class ColourPicker(QWidget):
  """ Widget to show a list of colour swatches and push buttons to pick a colour
  On picking, invokes a ComboPicker widget with n_picks closest options to provided colourList
  Callback function is passed to this widget
  """
  widget_file = files('GUI').joinpath('ColourPicker.ui')
  default_n_picks = 5

  def __init__(self, colourList, callback):
    super(ColourPicker, self).__init__()
    loadUi(self.widget_file, self) # Load the .ui file

    # Setup colour chart for fast fuzzy matching in colourList
    self.setup_colour_chart(colourList)
    # Setup dialog box
    self.setup_layout(colourList)
    # Store inputs for later
    self._colourList = colourList
    self._callback = callback

  def setup_layout(self, colourList):
    """Set up widget layout - a list of coloured swatches and a push button
    for each entry in colourList (can be 3 or 4 element colours, transparency ignored)
    Push buttons invoke the do_combine function with a colour number
    """
    # Setup coloured swatches
    #for num in range(len(colourList)):
    for num, cMatch in enumerate(colourList):

      # Make coloured swatch and place in grid
      match = QLabel()
      swatch = QPixmap(100, 20)
      cMatch = colourList[num]
      swatch.fill(QColor(cMatch[0], cMatch[1], cMatch[2]))
      match.setPixmap(swatch)

      self.gridLayout.addWidget(match, num+1, 1)
      match.adjustSize()

      # Make push button. Attach number in list as data. Place
      rButt = QPushButton(self)
      rButt.setProperty("colourNum", QVariant(num))
      rButt.setText("Combine With")
      rButt.clicked.connect(self.do_combine)
      self.gridLayout.addWidget(rButt, num+1, 2)

  def setup_colour_chart(self, colourList):
    """Create searcher object for fast fuzzy search on provided list.
    Resulting searcher can be invoked with item to match and count of
    how many matches to return. Matches returned in closeness order
    (see searcher.py for details)
    """
    self.searcher = buildTreeDirect(colourList)


  def do_combine(self):
    """Invoke ComboPicker dialog with selected item"""
    # Get sender's colour from list
    num = int(self.sender().property("colourNum"))
    item = self._colourList[num]

    # Get shortlist of closest matches for selection
    # +1 to include item itself and n_picks closest others
    shortList = self.searcher.find(item, self.default_n_picks+1)
    # Invoke Picker dialog
    picker = ComboPicker(item, shortList[1:], self._callback)
    picker.exec()


class ComboPicker(QDialog):
  """Dialog box hosting a ColourCombiner widget.
  Shortlist is passed to this widget. Callback is invoked with an
  ImageCombinePayload when dialog is dismissed
  """
  def __init__(self, item, shortList, callback):
    super(ComboPicker, self).__init__()

    # Store incoming selected colour and shortlist of closest others
    self._pickedColour = item
    self._colourList = shortList
    self._callback = callback

    # Create and show core picker widget
    self.pickerWidget = ColourCombiner(item, shortList)
    self.layout = QGridLayout()
    self.layout.addWidget(self.pickerWidget, 0,0)

    # Create button when selection is Done
    self.done_butt = QPushButton()
    self.done_butt.setText("Done")
    self.layout.addWidget(self.done_butt, 1,1)
    self.done_butt.clicked.connect(self.is_done)

    self.setLayout(self.layout)


  def is_done(self):
    """Invoke when selection is completed. Creates ImageCombinePayload
    from selection and invokes provided callback with this"""
    comboList = self.pickerWidget.get_selections()
    if len(comboList) > 0:
      payload = ImageCombinePayload(self._pickedColour, comboList)
      self._callback(payload)

    self.close()



class ColourCombiner(QWidget):
  """ Widget to show a list of colour swatches and pick several of them.
  Visual comparison with one specific colour is offered
  Assumes at least 2 matches (in UI file). Colours can be 3 or 4 element, transparency ignored
  """
  widget_file = files('GUI').joinpath('ColourCombiner.ui')

  def __init__(self, baseColour, colourList):
    super(ColourCombiner, self).__init__()
    loadUi(self.widget_file, self) # Load the .ui file

    self.setup_layout(baseColour, colourList)
    self._nItems = len(colourList)

  def setup_layout(self, inputColour, colourList):
    """ Setup a large swatch of inputColour, overlapped by swatches of
    each item in colourList, with a checkbox for each. Colour value is attached
    as data to checkbox
    """

    # Setup large inputColour swatch on left, spanning all grid spaces vertically
    # and two columns horizontally
    r,g,b = inputColour[0:3]
    swatch = QPixmap(250, 50*(len(colourList)+2))
    swatch.fill(QColor(r, g, b))
    self.inputSwatch.setPixmap(swatch)
    self.gridLayout.addWidget(self.inputSwatch, 1, 0, len(colourList), 2)
    self.inputSwatch.adjustSize()

    # Setup small colour swatches, checkboxes and data
    for num, cMatch in enumerate(colourList):
      # Create small swatch spanning 2 columns and overlapping large swatch
      match = QLabel()
      swatch = QPixmap(200, 50)
      swatch.fill(QColor(cMatch[0], cMatch[1], cMatch[2]))
      match.setPixmap(swatch)
      match.adjustSize()
      self.gridLayout.addWidget(match, num+1, 1, 1, 2)

      # Add checkbox with colour value attached as data
      rButt = QCheckBox(self)
      rButt.setProperty("colourVal", QVariant(cMatch))

      self.gridLayout.addWidget(rButt, num+1, 3)

  def get_selections(self):
    """Return a list of colour values for all selected checkboxes
    """

    selections = []
    for num in range(self._nItems):
      if self.gridLayout.itemAtPosition(num+1, 3).widget().isChecked():
        val = self.gridLayout.itemAtPosition(num+1, 3).widget().property("colourVal")
        selections.append(val)

    return selections


