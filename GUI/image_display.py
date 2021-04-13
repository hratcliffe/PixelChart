from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtWidgets import QGraphicsView, QGridLayout, QLabel
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
import PyQt5.QtCore as qtc
from PyQt5.QtCore import QSize
from PIL import ImageQt

#import KeepAspectRatio, SmoothTransformation

from ColourHandling import *
from .types import ImageStatePayload, ImageChangePayload

class ImageHandler(qtc.QObject):
  image_changed = qtc.pyqtSignal(ImageStatePayload, name="image_changed")

  def __init__(self, window):
    super(ImageHandler, self).__init__()
    self.window = window
    self.pane = window.image_pane
    self.image_hook = window.image_hook
    self.key_pane = window.key_box
    self.full_image = None
    self.key_layout = None

    
  def show_image_from_file(self, filename):

    self.full_image = imageExt.imageFromFile(filename)
    self.change_image(self.full_image)  
  
  def change_image(self, new_image):
  
    self.full_image = new_image
    tmp_im = self.full_image.getImage(opt=False)
    sz = tmp_im.size
    pixmap = tmp_im.toqpixmap()
    port_sz = self.pane.viewport().size()
    im_sz = qtc.QSize(sz[0], sz[1])
    im_sz.scale(port_sz, qtc.Qt.KeepAspectRatio)
    pixmap = pixmap.scaled(im_sz.width(), im_sz.height(), qtc.Qt.KeepAspectRatio, qtc.Qt.FastTransformation)
    self.image_hook.setPixmap(pixmap)
    self.image_hook.adjustSize()
    self.image_hook.show()

    im_cols = len(self.full_image.colourCounts)
    self.show_key()
    self.image_changed.emit(ImageStatePayload(im_sz, im_cols))
    

  def show_key(self):

    key = getKey(self.full_image)

    print(key)
    
    if self.key_layout is not None:
      clearLayout(self.key_layout)    
    
    else:
      self.key_layout = QGridLayout()
      self.key_pane.setLayout(self.key_layout)
      self.key_layout.setRowStretch(1, 0)
    
    cnt = 0
    for item in key:
      keyItem = QLabel(str(item[1]+1))

      badgeMap = item[2].toqpixmap()
      badgeMap = badgeMap.scaled(50, 50, qtc.Qt.KeepAspectRatio, qtc.Qt.FastTransformation)
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


  def resize_image(self):
    pass
    

  def modify_image(self, image, change_payload):
    """Modify the given image according to the given ImageChangePayload"""
  
    reduceColours(image, change_payload.n_cols)    
    self.change_image(image)
    self.show_key()

    
  #  @QtCore.pyqtSlot(ImageChangePayload)
  def on_image_change_request(self, value):
    self.modify_image(self.full_image, value)

  #  @QtCore.pyqtSlot(str)
  def on_save_triggered(self, filename):
    try:
      self.full_image.save(filename)
    except:
      pass

  #  @QtCore.pyqtSlot(PatternPayload)
  def on_pattern_save_triggered(self, value):
    
    filename = value.filename
    
    print(filename)
    
    printer = QPrinter(QPrinter.HighResolution)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(filename)
    
    painter = QPainter()
    painter.begin(printer)
    # Colour image
    
    rect = painter.viewport()
    
    o_sz = rect.size()
    
    tmp_im = self.full_image.getImage(opt=False)
    data = tmp_im.tobytes("raw", "RGB")
    sz = tmp_im.size
    sz1 = QSize(sz[0], sz[1])

    tmp_im = self.full_image.getImage(opt=False)
    data = tmp_im.tobytes("raw", "RGB")
    sz = tmp_im.size
    qimage = QImage(data, sz[0], sz[1], QImage.Format_RGB888) 
    pixmap = QPixmap.fromImage(qimage)
    
    sz1.scale(o_sz, qtc.Qt.KeepAspectRatio)
    sz1=QSize(sz1.width()*0.9, sz1.height()*0.9)
    rect.setSize(sz1)

    pixmap = pixmap.scaled(sz1.width(), sz1.height(), qtc.Qt.KeepAspectRatio, qtc.Qt.FastTransformation)

    
#    o_image = QImage(data, sz[0], sz[1], QImage.Format_RGB888) 
 #   painter.drawImage(rect, o_image)
    painter.drawPixmap(rect, pixmap)
    
    printer.newPage()
    # Symbolic image
    
    tmp_im = toSymbolicImage(self.full_image).getImage(opt=False)
    data = tmp_im.tobytes("raw", "RGB")
    sz = tmp_im.size
    sz1 = QSize(sz[0], sz[1])
    
    sz1.scale(o_sz, qtc.Qt.KeepAspectRatio)
    sz1=QSize(sz1.width()*0.9, sz1.height()*0.9)
    rect.setSize(sz1)
    
    o_image = QImage(data, sz[0], sz[1], QImage.Format_RGB888) 
    painter.drawImage(rect, o_image)
    
    printer.newPage()

    
    # Create key    
    
    # Handle descriptors
    
    # Save the lot (pdf?)
    
    
    painter.end()
    
    
def clearLayout(layout):
  # From https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt  or https://stackoverflow.com/a/10067548
  while layout.count():
    child = layout.takeAt(0)
    if child.widget():
      child.widget().deleteLater()
