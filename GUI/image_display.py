from PyQt5.QtGui import QFont
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import QGridLayout, QLabel
from PIL import ImageQt

from ColourHandling import imageExt
from ColourHandling.interfaceRoutines import *

from XStitchHeuristics.colours import colourChart
from Graphics.pattern import PatternGenerator
from .types import ImageStatePayload, ImageChangePayload, ImageSizePayload, PatternPayload, ImageCombinePayload, ImageEnhancePayload
from .warnings import PresaveDialog
from .recolour import RecolourDialog

class ImageHandler(QObject):
  image_changed = pyqtSignal(ImageStatePayload, name="image_changed")

  def __init__(self, window):
    super(ImageHandler, self).__init__()
    self.window = window
    self.pane = window.image_pane
    self.image_hook = window.image_hook
    self.key_pane = window.key_box
    self.full_image = None
    self.key_layout = None
    self.key = None
    self.pGen = PatternGenerator()
    
    self.cChart = colourChart()

  def get_image(self):
    return self.full_image
    
  def show_image_from_file(self, filename):

    self.full_image = imageExt.imageFromFile(filename)
    self.change_image(self.full_image)  
  
  def change_image(self, new_image):
  
    self.full_image = new_image
    
    pixmap = self.full_image.getImage(opt=False).toqpixmap()
    sz = pixmap.size()
    sz_b = pixmap.size()
    port_sz = self.pane.viewport().size()
    sz.scale(port_sz, Qt.KeepAspectRatio)
    scl = 0.95  #Scale down slightly to accomodate borders and things
    pixmap = pixmap.scaled(sz.width()*scl, sz.height()*scl, Qt.KeepAspectRatio, Qt.FastTransformation)

    self.image_hook.setPixmap(pixmap)
    self.image_hook.adjustSize()
    self.image_hook.show()

    im_cols = len(self.full_image.colourCounts)
    self.show_key(True)

    # Make sure this is backing image size, NOT pixmap size
    self.image_changed.emit(ImageStatePayload(sz_b, im_cols))
    
  def show_key(self, changed = False):

    # Get new key
    if changed:
      self.key = getKey(self.full_image)

    if self.key_layout is not None:
      clearLayout(self.key_layout)    
    
    else:
      self.key_layout = QGridLayout()
      self.key_pane.setLayout(self.key_layout)
      self.key_layout.setRowStretch(1, 0)
    
    cnt = 0
    for item in self.key:
      colourName = " ".join(item[4])
      keyItem = QLabel(colourName)
      keyItem.setFont(QFont("Arial", 10))
      
      badgeMap = item[2].toqpixmap()
      badgeMap = badgeMap.scaled(50, 50, Qt.KeepAspectRatio, Qt.FastTransformation)
      keyBadge = QLabel()
      keyBadge.setPixmap(badgeMap)
      keyBadge.adjustSize()

      self.key_layout.addWidget(keyItem, cnt, 0)
      self.key_layout.addWidget(keyBadge, cnt, 1)
      cnt = cnt + 1
      # Limit to showing 20 items
      if cnt > 20: 
        keyItem = QLabel("...")
        self.key_layout.addWidget(keyItem, cnt, 0)
        break

  def modify_image(self, image, change_payload):
    """Modify the given image according to the given ImageChangePayload"""
  
    reduceColours(image, change_payload.n_cols)

    recolourD = RecolourDialog(change_payload.opts["Palette"])
    recolourD.do_recolour(image)
    self.change_image(image)

  def enhance_image(self, image, enhance_payload):
    """Modify the given image according to the given ImageEnhancePayload"""

    # Simple divide-by-zero protection below so use this if to ensure no change in value -> no change in image
    if(enhance_payload.newValue == enhance_payload.oldValue): return

    # TODO sensible scaling from say 0.1 to 10x???
    if(enhance_payload.attr == "br"):
        new_bright = enhance_payload.newValue/(enhance_payload.oldValue+1)
        adjustBrightness(image, new_bright)
    elif(enhance_payload.attr == "co"):
        new_con = enhance_payload.newValue/(enhance_payload.oldValue+1)
        adjustContrast(image, new_con)
    elif(enhance_payload.attr == "sat"):
        new_sat = enhance_payload.newValue/(enhance_payload.oldValue+1)
        adjustSaturation(image, new_sat)
    else:
        raise ValueError("Invalid enhancement {}".format(enhance_payload.attr))

    self.change_image(image)

  def modify_image_advanced(self, image, combine_payload):
    """Modify the given image according to the given ImageCombinePayload"""
  
    recolourFromList(image, combine_payload.new, combine_payload.original)
    self.change_image(image)
    

  def resize_image(self, image, resize_payload):
    """Modify the given image according to the given ImageResizePayload"""
    
    resizeImage(image, resize_payload.width, resize_payload.height)
    self.change_image(image)

  def pattern_checks(self, details):
    # Show pattern details and verify anything "suspicious"
    
    checks = self.pGen.checks(details, self.full_image.getImage(opt=False).size, len(self.full_image.colourCounts))

    checkDialog = PresaveDialog()
    checkDialog.fill_warnings(checks["warnings"])
    checkDialog.fill_settings(checks["settings"])
    checkDialog.show()

    return checkDialog.exec_() 
    
  @pyqtSlot(ImageChangePayload)
  def on_image_change_request(self, value):
    if self.full_image:
      self.modify_image(self.full_image, value)

  @pyqtSlot(ImageEnhancePayload)
  def on_image_enhance_request(self, value):
    self.enhance_image(self.full_image, value)
  @pyqtSlot(ImageCombinePayload)
  def on_image_combine_request(self, value):
    self.modify_image_advanced(self.full_image, value)

  @pyqtSlot(ImageSizePayload)
  def on_image_resize_request(self, value):
    if self.full_image:
      self.resize_image(self.full_image, value)


  @pyqtSlot(str)
  def on_save_triggered(self, filename):
    try:
      self.full_image.save(filename)
    except:
      pass

  @pyqtSlot(PatternPayload)
  def on_pattern_save_triggered(self, value):
    
    cont = self.pattern_checks(value.details)
    if not cont:
      return

    # self.key was filled last time image was changed
    self.pGen.save(value.filename, value.details, self.full_image, self.key, self.cChart)
    
def clearLayout(layout):
  # From https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt  or https://stackoverflow.com/a/10067548
  while layout.count():
    child = layout.takeAt(0)
    if child.widget():
      child.widget().deleteLater()
