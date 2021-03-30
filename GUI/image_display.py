from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QGraphicsView
import PyQt5.QtCore as qtc
#import KeepAspectRatio, SmoothTransformation

from ColourHandling import *


class ImageHandler():

  def __init__(self, window):
    self.window = window
    self.pane = window.image_pane
    self.image_hook = window.image_hook
    
  def change_image(self, filename):
  
    self.full_image = imageExt.imageFromFile(filename)
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

    