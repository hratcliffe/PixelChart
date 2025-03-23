from PyQt6.QtGui import QFont, QPixmap, QColor
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, Qt, QEvent, QPointF
from PyQt6.QtWidgets import QGridLayout, QLabel
from PIL import ImageQt

from ColourHandling import imageExt
from ColourHandling.interfaceRoutines import *

from XStitchHeuristics.colours import colourChart
from Graphics.pattern import PatternGenerator
from .types import ImageStatePayload, ImageChangePayload, ImageSizePayload, PatternPayload, ImageCombinePayload, ImageEnhancePayload
from .warnings import PresaveDialog
from .recolour import RecolourDialog

from math import floor

_max_key_items = 20


# TODO This is a bit of a God object. Should some functions be delegated to something else?

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

    #Mouse tracking over image
    self.image_hook.setMouseTracking(True)
    self.image_hook.installEventFilter(self)

    self.colourPatch = window.swatch

  def check_for_image(self):
    return self.full_image is not None

  def get_image(self):
    if(self.full_image):
      return self.full_image
    else:
      raise ValueError

  def show_image_from_file(self, filename):

    self.full_image = imageExt.imageFromFile(filename)
    self.change_image(self.full_image)

  def change_image(self, new_image):

    self.full_image = new_image

    pixmap = self.full_image.getImage(opt=False).toqpixmap()
    sz = pixmap.size()
    sz_b = pixmap.size()
    port_sz = self.pane.viewport().size()
    sz.scale(port_sz, Qt.AspectRatioMode.KeepAspectRatio)
    scl = 0.95  #Scale down slightly to accomodate borders and things
    pixmap = pixmap.scaled(int(sz.width()*scl), int(sz.height()*scl), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)

    self.image_hook.setPixmap(pixmap)
    self.image_hook.adjustSize()
    self.image_hook.show()

    #Store relative scale between image and pixmap
    self.pixmap_scl = new_image.size()[0]/pixmap.size().width()

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
      badgeMap = badgeMap.scaled(50, 20, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation)
      keyBadge = QLabel()
      keyBadge.setPixmap(badgeMap)
      keyBadge.adjustSize()

      self.key_layout.addWidget(keyItem, cnt, 0)
      self.key_layout.addWidget(keyBadge, cnt, 1)
      cnt = cnt + 1
      # Limit to showing capped number of items
      if cnt > _max_key_items:
        keyItem = QLabel("...")
        self.key_layout.addWidget(keyItem, cnt, 0)
        break

  def modify_image(self, image, change_payload):
    """Modify the given image according to the given ImageChangePayload"""

    if(change_payload.opts["Emphasize"] != '0'):
      reduceColours(image, n_cols=change_payload.n_cols, emph=change_payload.opts["Emphasize"])
    else:
      reduceColours(image, n_cols=change_payload.n_cols)

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

    return checkDialog.exec()

  @pyqtSlot(ImageChangePayload)
  def on_image_change_request(self, value):
    if self.full_image:
      self.modify_image(self.full_image, value)
  @pyqtSlot(ImageEnhancePayload)
  def on_image_enhance_request(self, value):
    if self.full_image:
      self.enhance_image(self.full_image, value)
  @pyqtSlot(ImageCombinePayload)
  def on_image_combine_request(self, value):
    if self.full_image:
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

  def eventFilter(self, widget, event):
    if event.type() == QEvent.Type.MouseButtonPress:
      pos = event.position()
      self.showColourAtPosition(pos)

    return super().eventFilter(widget, event)

  def showColourAtPosition(self, position):
    #Position relative to image_hook, figures out the scaling and looks up in the ORIGINAL image
    s_pos = position * self.pixmap_scl
    # Floor - select the pixel we're within
    n_pos = QPointF(floor(s_pos.x()), floor(s_pos.y()))

    colour = self.full_image.getColourAt(n_pos)
    if colour:
      swatch = QPixmap(100, 20)
      swatch.fill(QColor(colour[0], colour[1], colour[2]))
      self.colourPatch.setPixmap(swatch)

def clearLayout(layout):
  # From https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt  or https://stackoverflow.com/a/10067548
  while layout.count():
    child = layout.takeAt(0)
    if child.widget():
      child.widget().deleteLater()
