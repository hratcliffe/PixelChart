from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QFileDialog

from importlib_resources import files
from copy import deepcopy

from os import path

from .types import ImageStatePayload, PatternPayload, ImageSizePayload
from .warnings import WarnDialog

class FileLoader(QObject):

  save_triggered = pyqtSignal(str, name="save_triggered")
  pattern_save_triggered = pyqtSignal(PatternPayload, name="pattern_save_triggered")

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


class FileDetailsHandler(QObject):

  image_resize_request = pyqtSignal(ImageSizePayload, name="image_resize_request")

  def __init__(self, window):
    super(FileDetailsHandler, self).__init__()

    self.extras_dict = {"RGBCodes":False, "ColourNumbers":False, "LengthEstimates":False,    "FinalSize":False}
    self.window = window
  
    fill_file_combos(window)
    setup_file_info(window, "dummy.jpg")
    
    self.extras_button = window.extras_button
    self.extras_button.clicked.connect(self.extras_button_clicked) 

    self.resize_button = window.resize_button
    self.resize_button.clicked.connect(self.resize_button_clicked) 

    self.ht_adj_slider = window.ht_adj_slider
    self.wid_adj_slider = window.wid_adj_slider
    self.wid_adj_slider.valueChanged.connect(self.wid_slider_changed)
    self.ht_adj_slider.valueChanged.connect(self.ht_slider_changed)
    
    # Set to 0 or higher for force aspect preserve, -ve will ignore any aspect locking. If 0 here, then wont be applied until first image is loaded
    self.aspect_ratio = 0

  def extras_button_clicked(self):
    extrasDialog = FileExtras(self.extras_dict)
    extrasDialog.connect_checks(self.needs_key)
    extrasDialog.exec_()
    self.extras_dict = extrasDialog.get_selections()

  def resize_button_clicked(self):
    width = self.wid_adj_slider.value()
    ht = self.ht_adj_slider.value()
    self.image_resize_request.emit(ImageSizePayload(width, ht))

  def wid_slider_changed(self):
    self.set_resize_slider_labels(wid=self.wid_adj_slider.value())
    if self.aspect_ratio > 0:
      # DO NOT allow to emit value changed or will infinite loop
      val = self.ht_adj_slider.blockSignals(True)
      self.ht_adj_slider.setValue(self.wid_adj_slider.value()/self.aspect_ratio)
      self.set_resize_slider_labels(ht=self.ht_adj_slider.value())
      self.ht_adj_slider.blockSignals(val)

  def ht_slider_changed(self):
    self.set_resize_slider_labels(ht=self.ht_adj_slider.value())
    if self.aspect_ratio > 0:
      # DO NOT allow to emit value changed or will infinite loop
      val = self.wid_adj_slider.blockSignals(True)
      self.wid_adj_slider.setValue(self.ht_adj_slider.value()*self.aspect_ratio)
      self.set_resize_slider_labels(wid=self.wid_adj_slider.value())
      self.wid_adj_slider.blockSignals(val)


  def fill_filename(self, name):
    short_name = path.basename(name)
    self.window.filename_show.setText(short_name)
    self.window.filename_show.setToolTip(name)

  def set_resize_sliders(self, wid, ht):
    self.window.wid_adj_slider.setValue(wid)
    self.window.ht_adj_slider.setValue(ht)

    if self.aspect_ratio >= 0: self.aspect_ratio = wid/ht
    
  def set_resize_slider_labels(self, wid=None, ht=None):

    if wid:
      self.window.wid_label.setText(str(wid))
    if ht:
      self.window.ht_label.setText(str(ht))

  def get_details(self):
    details = deepcopy(self.extras_dict)
    
    details["Symbols"] = self.window.symbols_check.isChecked()
    details["Key"] = self.window.key_check.isChecked()
    details["Gauge"] = self.window.gauge_box.currentData()
    details["PTitle"] = self.window.pattern_title_edit.text()
    details["PText"] = self.window.pattern_text_edit.toPlainText()
        
    return details
        

  @pyqtSlot(ImageStatePayload)
  def on_image_changed(self, value):
    self.set_resize_sliders(value.sz.width(), value.sz.height())

  def needs_key(self, value):
    # Use to enable key when extras are picked
    if value:
      self.window.key_check.setChecked(1)

class FileExtras(QDialog):
  dialog_file = files('GUI').joinpath('ExtrasDialog.ui')

  def __init__(self, selections={}):
    super(FileExtras, self).__init__()
    loadUi(self.dialog_file, self)
    
    try:
      if selections["RGBCodes"]:
        self.rgb_check.setChecked(True) 
    except:
      pass
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
    select["RGBCodes"] = self.rgb_check.isChecked()    
    select["ColourNumbers"] = self.colour_check.isChecked()    
    select["LengthEstimates"] = self.length_check.isChecked()    
    select["FinalSize"] = self.size_check.isChecked()    
    return select

  def connect_checks(self, slot):
  
    self.rgb_check.stateChanged.connect(slot)
    #self.colour_check.stateChanged.connect(slot)


def setup_file_info(window, name):

  window.filename_show.setText((name))
  
def fill_file_combos(window):

  window.gauge_box.addItem("14", 14)
  window.gauge_box.addItem("16", 16)
  window.gauge_box.addItem("18", 18)

