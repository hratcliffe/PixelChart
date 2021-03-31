from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QLabel, QDialog, QFileDialog
import PyQt5.QtCore as qtc
from importlib_resources import files
from copy import deepcopy

from os import path
import sys

from ColourHandling.detect import mergeColours
from .types import ImageStatePayload, ImageChangePayload


_default_reduce_number = 20

class ColourOptionsHandler(qtc.QObject):
  image_change_request = qtc.pyqtSignal(ImageChangePayload, name="image_change_request")

  def __init__(self, window):
    super(ColourOptionsHandler, self).__init__()

    self.window = window
  
    fill_colour_combos(window)
    
    self.go_button = window.colour_go_button
    self.go_button.clicked.connect(self.go_button_clicked) 

  def set_num_colours(self, num):
    # Shows current number and number to reduce to. Latter is capped at current number, and is set to lower of current and default
  
    self.window.current_cols.setText(str(num))
    self.window.colour_num_select.setMaximum(num)
    
    #Recommended number default - allow m
    if num > _default_reduce_number:
      self.window.colour_num_select.setValue(_default_reduce_number)
    else:
      self.window.colour_num_select.setValue(num)
      

  def go_button_clicked(self):
    # Extract colour options
    num = self.window.colour_num_select.value()
    
    vals = {"Emphasize": self.window.emphasize_select.currentData(), "Optimize": self.window.optimize_select.currentData()}
    
    self.image_change_request.emit(ImageChangePayload(num, opts=vals))
        

#  @QtCore.pyqtSlot(ImageStatePayload)
  def on_image_changed(self, value):
    self.set_num_colours(value.n_cols)


def fill_colour_combos(window):
  
  window.emphasize_select.addItem("None", '0')      
  window.emphasize_select.addItem("Red", 'r')      
  window.emphasize_select.addItem("Blue", 'b')    
  window.emphasize_select.addItem("Green", 'g')
  window.emphasize_select.addItem("Lines", 'l')
  window.emphasize_select.addItem("Brights", 'h')    
  window.emphasize_select.addItem("Shade", 's')

  window.optimize_select.addItem("None", '0')    
  window.optimize_select.addItem("Landscape", 'l')    
  window.optimize_select.addItem("Portrait", 'p')    
  window.optimize_select.addItem("Object", 'o')
  
