from PyQt5.QtWidgets import QDialog, QWidget, QLabel, QPushButton, QRadioButton, QGridLayout, QCheckBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import QVariant

from ColourHandling.interfaceRoutines import makeSwatch
from XStitchHeuristics.colours import colourChart, colourItem
from General.searcher import *
from .types import ImageCombinePayload


from importlib_resources import files
from PIL.ImageQt import toqpixmap
from re import match as re_match

class ColourPicker(QWidget):
  widget_file = files('GUI').joinpath('ColourPicker.ui')
  default_n_picks = 5

  def __init__(self, colourList, callback):
    super(ColourPicker, self).__init__()
    loadUi(self.widget_file, self) # Load the .ui file
    
    self.setup_colour_chart(colourList)
    self.setup_layout(colourList)
    self._colourList = colourList
    self._callback = callback
        
  def setup_layout(self, colourList):

    # Setup coloured swatches
    for num in range(len(colourList)):

      match = QLabel()
      
      swatch = QPixmap(100, 20)
      cMatch = colourList[num]
      swatch.fill(QColor(cMatch[0], cMatch[1], cMatch[2]))
      match.setPixmap(swatch)
      
      self.gridLayout.addWidget(match, num+1, 1)
      match.adjustSize()

      rButt = QPushButton(self)
      rButt.setProperty("colourNum", QVariant(num))
      rButt.setText("Combine With")
      rButt.clicked.connect(self.do_combine)
      self.gridLayout.addWidget(rButt, num+1, 2)

  def setup_colour_chart(self, colourList):
    self.searcher = buildTreeDirect(colourList) 


  def do_combine(self):
    # Get sender's colour and show combiner widget
    num = int(self.sender().property("colourNum"))
    item = self._colourList[num]

    shortList = self.searcher.find(item, self.default_n_picks+1)
    picker = ComboPicker(item, shortList[1:], self._callback)
    picker.exec_()

def _subs(text, sub):
  # Substitue sub into text where FIRST <> are found. If there are more than one pair, can call repeatedly and will subs from left to right

  try:
    res = re_match(r"(.*)<.*>(.*)", text)
    new_str = [res.group(1), sub, res.group(2)]
  
    return ''.join(new_str)
  except:
    return text

# New modal window to pick combos. Mostly dialog to host Combiner widget
class ComboPicker(QDialog):

  def __init__(self, item, shortList, callback):
    super(ComboPicker, self).__init__() 
    
    self._pickedColour = item
    self._colourList = shortList
    self._callback = callback

    self.pickerWidget = ColourCombiner(item, shortList)
    
    self.layout = QGridLayout()
    self.layout.addWidget(self.pickerWidget, 0,0)
    
    self.done_butt = QPushButton()
    self.done_butt.setText("Done")
    self.layout.addWidget(self.done_butt, 1,1)
        
    self.setLayout(self.layout)

    self.done_butt.clicked.connect(self.is_done)


  def is_done(self):
    comboList = self.pickerWidget.get_selections()
    if len(comboList) > 0:
      payload = ImageCombinePayload(self._pickedColour, comboList)
      self._callback(payload)
    
    self.close()
    


# UI file assumes at least 2 matches will be offered, which is true in general
class ColourCombiner(QWidget):
  widget_file = files('GUI').joinpath('ColourCombiner.ui')

  def __init__(self, baseColour, colourList):
    super(ColourCombiner, self).__init__()
    loadUi(self.widget_file, self) # Load the .ui file
    
    self.setup_layout(baseColour, colourList)
    self._nItems = len(colourList)
        
  def setup_layout(self, inputColour, colourList):

    r,g,b = inputColour[0:3]
    swatch = QPixmap(250, 50*(len(colourList)+2))
    swatch.fill(QColor(r, g, b))
    self.inputSwatch.setPixmap(swatch)
    # Add widget will remove and re-add
    self.gridLayout.addWidget(self.inputSwatch, 1, 0, len(colourList), 2)
    self.inputSwatch.adjustSize()


    # Setup colour swatches, checkboxes and codes
    for num, cMatch in enumerate(colourList):
      match = QLabel()
      swatch = QPixmap(200, 50)
      swatch.fill(QColor(cMatch[0], cMatch[1], cMatch[2]))
      match.setPixmap(swatch)
      match.adjustSize()
      self.gridLayout.addWidget(match, num+1, 1, 1, 2)

      rButt = QCheckBox(self)
      rButt.setProperty("colourVal", QVariant(cMatch))

      self.gridLayout.addWidget(rButt, num+1, 3) 

  def get_selections(self):

    selections = []
    for num in range(self._nItems):
      if self.gridLayout.itemAtPosition(num+1, 3).widget().isChecked():
        val = self.gridLayout.itemAtPosition(num+1, 3).widget().property("colourVal")
        col = (int(val[0]), int(val[1]), int(val[2]))
        if len(val) > 3:
          # Transparency
          col = (col[0], col[1], col[2], int(val[3]))
        selections.append(col)

    return selections


