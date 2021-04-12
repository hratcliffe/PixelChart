from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QLabel, QDialog, QFileDialog
import PyQt5.QtCore as qtc

from importlib_resources import files
from copy import deepcopy

from os import path
import sys

from .types import ImageStatePayload, PatternPayload
from .warnings import WarnDialog

class FileLoader(qtc.QObject):

  save_triggered = qtc.pyqtSignal(str, name="save_triggered")
  pattern_save_triggered = qtc.pyqtSignal(PatternPayload, name="pattern_save_triggered")

  def __init__(self, window, fileH):
    super(FileLoader, self).__init__()

    window.LoadButton.clicked.connect(self.load_file)   
    window.SaveButton.clicked.connect(self.save_file)
    window.PatternButton.clicked.connect(self.save_pattern)
 
    self.window = window
    self.details = fileH
    self.jpg_warning_dismissed = False

  def load_file(self):
  
    loader = QFileDialog()
    loader.setFileMode(QFileDialog.ExistingFile)    
    loader.show()
    if(loader.exec_()):
      filename = loader.selectedFiles()[0]
      self.details.fill_filename(filename)
      self.window.load_triggered(filename)


  def save_file(self):
  
    loader = QFileDialog()
    loader.setAcceptMode(QFileDialog.AcceptSave)
    loader.setFileMode(QFileDialog.AnyFile)    
    loader.show()
    if(loader.exec_()):
      filename = loader.selectedFiles()[0]
      root, ext = path.splitext(filename)
      new_ext = '.png'
      if not self.jpg_warning_dismissed and ext == ".jpg":
        dialog = WarnDialog()
        dialog.set_message("Warning: jpg format may introduce new colours. Recommend saving as png instead")  
        dialog.set_options(new_ext, ".jpg")
        dialog.show()
        if dialog.exec_():
          filename = root + new_ext
      
        self.jpg_warning_dismissed = dialog.check_dontAskState()
      
      self.save_triggered.emit(filename)
    

  def save_pattern(self):
  
    loader = QFileDialog()
    loader.setAcceptMode(QFileDialog.AcceptSave)
    loader.setFileMode(QFileDialog.AnyFile)    
    loader.show()
    if(loader.exec_()):
      filename = loader.selectedFiles()[0]
      stuff = self.details.get_details()
      self.pattern_save_triggered.emit(PatternPayload(filename, stuff))


class FileDetailsHandler(qtc.QObject):

  def __init__(self, window):
    super(FileDetailsHandler, self).__init__()

    self.extras_dict = {"ColourNumbers":False, "LengthEstimates":False,    "FinalSize":False}
    self.window = window
  
    fill_file_combos(window)
    setup_file_info(window, "dummy.jpg")
    
    self.extras_button = window.extras_button
    self.extras_button.clicked.connect(self.extras_button_clicked) 

  def extras_button_clicked(self):
    extrasDialog = FileExtras(self.extras_dict)
    extrasDialog.exec_()
    self.extras_dict = extrasDialog.get_selections()

  def fill_filename(self, name):
    short_name = path.basename(name)
    self.window.filename_show.setText(short_name)
    self.window.filename_show.setToolTip(name)

  def set_resize_sliders(self, wid, ht):
    self.window.wid_adj_slider.setValue(wid)
    self.window.ht_adj_slider.setValue(ht)
    self.window.wid_label.setText(str(wid))
    self.window.ht_label.setText(str(ht))

  def get_details(self):
    details = deepcopy(self.extras_dict)
    
    details["Symbols"] = self.window.symbols_check.isChecked()
    details["Key"] = self.window.key_check.isChecked()
    details["Gauge"] = self.window.gauge_box.currentData()
    
    return details
        

#  @QtCore.pyqtSlot(ImageStatePayload)
  def on_image_changed(self, value):
    self.set_resize_sliders(value.sz.width(), value.sz.height())


class FileExtras(QDialog):
  dialog_file = files('GUI').joinpath('ExtrasDialog.ui')

  def __init__(self, selections={}):
    super(FileExtras, self).__init__() # Call the inherited classes __init__ method
    uic.loadUi(self.dialog_file, self) # Load the .ui file
    
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

  window.gauge_box.addItem("14", 14)
  window.gauge_box.addItem("16", 16)
  window.gauge_box.addItem("18", 18)

