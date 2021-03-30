from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QLabel, QDialog
from importlib_resources import files

import sys

class FileHandler():

  def __init__(self, window):

    self.extras_dict = {}
  
    fill_file_combos(window)
    setup_file_info(window, "dummy.jpg")
    
    self.extras_button = window.extras_button
    self.extras_button.clicked.connect(self.extras_button_clicked) 


  def extras_button_clicked(self):
    # SHould this dialog be modal or not??
    
    extrasDialog = FileExtras(self.extras_dict)
    extrasDialog.exec_()
    
    self.extras_dict = extrasDialog.get_selections()
    print(self.extras_dict)


class FileExtras(QDialog):
  dialog_file = files('GUI').joinpath('ExtrasDialog.ui')

  def __init__(self, selections={}):
    print("Showing Dialog")
    super(FileExtras, self).__init__() # Call the inherited classes __init__ method
    uic.loadUi(self.dialog_file, self) # Load the .ui file
    
    print(selections)
    try:
      if selections["ColourNumbers"]:
        self.colour_check.setChecked(True) 
    except:
      pass
    try:
      if selections["LengthEstimates"]:
        self.length_check.setChecked(True) 
    except:
      pass
    try:
      if selections["FinalSize"]:
        self.size_check.setChecked(True) 
    except:
      pass
        
    self.show() # Show the GUI

  def get_selections(self):
    
    select = {}
    select["ColourNumbers"] = self.colour_check.isChecked()    
    select["LengthEstimates"] = self.length_check.isChecked()    
    select["FinalSize"] = self.size_check.isChecked()    
    return select



def setup_file_info(window, name):

  window.filename_show.setText((name))
  
def fill_file_combos(window):

  window.gauge_box.addItem("14")
  window.gauge_box.addItem("16")
  window.gauge_box.addItem("18")

