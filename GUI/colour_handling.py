from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QLabel, QDialog, QFileDialog
from importlib_resources import files
from copy import deepcopy

from os import path
import sys

class ColourOptionsHandler():

  def __init__(self, window):

    self.window = window
  
    fill_colour_combos(window)
    
    self.go_button = window.colour_go_button
    self.go_button.clicked.connect(self.go_button_clicked) 

  def go_button_clicked(self):
    pass
    

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
  
