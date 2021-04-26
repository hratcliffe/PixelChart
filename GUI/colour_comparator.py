from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5 import uic
from PyQt5 import QtCore as qtc

from ColourHandling.interfaceRoutines import *
from XStitchHeuristics.colours import colourChart, colourItem

from importlib_resources import files
from PIL import ImageQt
import re

# UI file assumes at least 2 matches will be offered, which is true in general
class ColourComparator(QWidget):
  widget_file = files('GUI').joinpath('ColourComparator.ui')

  def __init__(self):
    super(ColourComparator, self).__init__()
    uic.loadUi(self.widget_file, self) # Load the .ui file
    
    self.cChart = colourChart()
    self.setup_layout()
    self.show()
        
  def setup_layout(self, inputColour=(200,0,0), nMatches=8):
    # Test - use some random colour

    self.iColourLabel.setText(_subs(self.iColourLabel.text(), str(inputColour)))
    self.matchLabel.setText(_subs(self.matchLabel.text(), self.cChart.brand))


    r,g,b = inputColour
    matches = self.cChart.matchColour(colourItem(r,g,b), nMatches)

    for num, cMatch in enumerate(matches):

      match = QLabel()
      iSwatch = makeSwatch(cMatch.rgb)
      
      swatch = iSwatch.toqpixmap()
      swatch = swatch.scaled(200, 50, qtc.Qt.IgnoreAspectRatio, qtc.Qt.FastTransformation)
      match.setPixmap(swatch)
      self.gridLayout.addWidget(match, num+1, 1, 1, 2)
      match.adjustSize()
      label = QLabel("{} - {}".format(cMatch.num, cMatch.name))
      self.gridLayout.addWidget(label, num+1, 3, 1, 1)


    # Set input swatch and adjust to fit
    iSwatch = makeSwatch(inputColour)  
    swatch = iSwatch.toqpixmap()
    swatch = swatch.scaled(200, 50*(len(matches)+2), qtc.Qt.IgnoreAspectRatio, qtc.Qt.FastTransformation)

    self.inputSwatch.setPixmap(swatch)

    # Add widget will remove and re-add
    self.gridLayout.addWidget(self.inputSwatch, 1, 0, len(matches), 2)
    self.inputSwatch.adjustSize()

def _subs(text, sub):
  # Substitue sub into text where FIRST <> are found. If there are more than one pair, can call repeatedly and will subs from left to right
  res = re.match(r"(.*)<.*>(.*)", text)
  new_str = [res.group(1), sub, res.group(2)]
  
  return ''.join(new_str)
