from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QGraphicsView
import PyQt5.QtCore as qtc
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

    
  def show_image_from_file(self, filename):

    self.full_image = imageExt.imageFromFile(filename)
    self.change_image(self.full_image)
  
  
  def change_image(self, new_image):
  
    self.full_image = new_image
    data = self.full_image.coreImage.tobytes("raw", "RGB")
    sz = self.full_image.coreImage.size
    self.qimage = QImage(data, sz[0], sz[1], QImage.Format_RGB888) 
    pixmap = QPixmap.fromImage(self.qimage)
    port_sz = self.pane.viewport().size()
    im_sz = qtc.QSize(sz[0], sz[1])
    im_sz.scale(port_sz, qtc.Qt.KeepAspectRatio)
    pixmap = pixmap.scaled(im_sz.width(), im_sz.height(), qtc.Qt.KeepAspectRatio, qtc.Qt.FastTransformation)
    self.image_hook.setPixmap(pixmap)
    self.image_hook.adjustSize()
    self.image_hook.show()

    im_cols = len(self.full_image.colourCounts)
    self.image_changed.emit(ImageStatePayload(im_sz, im_cols))
    

  def resize_image(self):
    pass
    

  def modify_image(self, image, change_payload):
    """Modify the given image according to the given ImageChangePayload"""
  
    new_image = mergeColours(image.coreImage, change_payload.n_cols)
    # TODO this is pretty clumsy...
    image.setImage(new_image)
    self.change_image(image)
    
  #  @QtCore.pyqtSlot(ImageChangePayload)
  def on_image_change_request(self, value):
    self.modify_image(self.full_image, value)
    
    