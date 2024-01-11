from PyQt5.QtWidgets import QWidget, QLabel, QRadioButton
from PyQt5.uic import loadUi
from PyQt5.QtGui import QKeySequence, QPixmap, QColor

from XStitchHeuristics.colours import colourChart, colourItem

from importlib_resources import files
from PIL.ImageQt import toqpixmap
from re import match as re_match

# UI file assumes at least 2 matches will be offered, which is true in general
class ColourComparator(QWidget):
  """ Widget to select closest match colours from pre-specified list.
  Will show a list of colour swatches and pick one of them.
  Visual comparison with one specific colour (not necessarily in specified list) is offered
  Assumes at least 2 matches (in UI file). Colours can be 3 or 4 element, transparency ignored
  """

  widget_file = files('GUI').joinpath('ColourComparator.ui')

  def __init__(self, chart ="DMC", nMatches=8):
    super(ColourComparator, self).__init__()
    loadUi(self.widget_file, self) # Load the .ui file

    # Select colour chart by name
    self.cChart = colourChart(chart)
    self.setup_layout(nMatches)

  def setup_layout(self, nMatches):
    """ Setup blank (uncoloured) layout
    Setup a large swatch of one 'colour', overlapped by nMatches swatches,
    with a radio button for each.
    """
    # NOTE: shortcut keys will only work with up to 9 matches!

    self.nMatches = nMatches

    self.matchLabel.setText(_subs(self.matchLabel.text(), self.cChart.brand))

    # Setup blank swatches, radio buttons and blank names
    for num in range(self.nMatches):

      match = QLabel()
      self.gridLayout.addWidget(match, num+1, 1, 1, 2)
      match.adjustSize()
      label = QLabel("")
      self.gridLayout.addWidget(label, num+1, 4, 1, 1)
      rButt = QRadioButton(self)
      rButt.setText(str(num+1)+')')
      rButt.setShortcut(QKeySequence(str(num+1)))
      if num == 0: rButt.setChecked(True)
      rButt.clicked.connect(self.selected)
      self.gridLayout.addWidget(rButt, num+1, 3)

  def show_colour(self, inputColour):
    """ Populate layout for given colour. Large swatch is coloured with inputColour,
    smaller with closest matches from self.cChart. Swatches are labelled by number,
    and shortcut keys added by number. Swatches also labelled by name provided by cChart
    Repeated calls to this function are valid and all data is reset
    """

    self.iColourLabel.setText(_subs(self.iColourLabel.text(), str(inputColour)))

    r,g,b = inputColour[0:3]
    # Get closest matches from cChart and store for later
    matches = self.cChart.matchColour(colourItem(r,g,b), self.nMatches)
    self.lastMatches = matches

    # Set input swatch and adjust to fit. This goes behind the match swatches
    swatch = QPixmap(250, 50*(len(matches)+2))
    swatch.fill(QColor(r, g, b))
    self.inputSwatch.setPixmap(swatch)

    # Add widget will remove and re-add on repeated function invocation
    self.gridLayout.addWidget(self.inputSwatch, 1, 0, len(matches), 2)
    self.inputSwatch.adjustSize()

    for num, cMatch in enumerate(matches):
      swatch = QPixmap(200, 50)
      swatch.fill(QColor(cMatch.rgb[0], cMatch.rgb[1], cMatch.rgb[2]))
      match = self.gridLayout.itemAtPosition(num+1, 1).widget()
      match.setPixmap(swatch)
      match.adjustSize()

      label = self.gridLayout.itemAtPosition(num+1, 4).widget()
      label.setText("{} - {}".format(cMatch.num, cMatch.name))

    # Set/Reset radio button and set selection value to 1st
    self.gridLayout.itemAtPosition(1,3).widget().setChecked(True)
    self.lastSelection = 1


  def selected(self, val):
    """Store selection value when a new button becomes selected"""
    # TODO swap from text to radioButton data property?
    selection = int(self.sender().text().strip(')'))
    self.lastSelection = selection

  def get_selected(self):
    """ Return tuple of selection number and its colour value
    """
    # TODO swap from text to radioButton data property?
    return (self.lastSelection, self.lastMatches[self.lastSelection-1])

def _subs(text, sub):
  # Substitue sub into text where FIRST <> are found. If there are more than one pair, can call repeatedly and will subs from left to right

  try:
    res = re_match(r"(.*)<.*>(.*)", text)
    new_str = [res.group(1), sub, res.group(2)]

    return ''.join(new_str)
  except:
    return text
