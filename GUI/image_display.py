from PyQt5.QtGui import QPixmap, QImage, QPainter, QFont, QIcon
from PyQt5.QtWidgets import QGraphicsView, QGridLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
import PyQt5.QtCore as qtc
from PyQt5.QtCore import QSize
from PIL import ImageQt

#import KeepAspectRatio, SmoothTransformation

from ColourHandling import *
from .types import ImageStatePayload, ImageChangePayload
from .warnings import PresaveDialog

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
    self.key = None

    
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
    self.show_key(True)

    # Make sure this is backing image size, NOT pixmap size
    b_im_sz = qtc.QSize(sz[0], sz[1])
    self.image_changed.emit(ImageStatePayload(b_im_sz, im_cols))
    
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
      colourName = item[4]
      keyItem = QLabel(colourName)
      keyItem.setFont(QFont("Arial", 10))
      
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

  def modify_image(self, image, change_payload):
    """Modify the given image according to the given ImageChangePayload"""
  
    reduceColours(image, change_payload.n_cols)    
    self.change_image(image)

  def resize_image(self, image, resize_payload):
    """Modify the given image according to the given ImageResizePayload"""
    
    resizeImage(image, resize_payload.width, resize_payload.height)
    self.change_image(image)

  def pattern_checks(self):
    # Show pattern details and verify anything "suspicious"
    
    # Use constants so we can make these configurable later
    max_sz = (200, 200)
    max_colours = 50
        
    warnings = []

    im_sz = self.full_image.getImage(opt=False).size
    if im_sz[0] > max_sz[0] or im_sz[1] > max_sz[1]:
      warnings.append("Image size is very large ({} x {})".format(im_sz[0], im_sz[1]))

    im_cols = len(self.full_image.colourCounts)
    if im_cols > max_colours:
      warnings.append("Number of colours is very large ({}). Symbolic pattern will have repeats!".format(im_cols))
      
    setts = []

    
    checkDialog = PresaveDialog()
    checkDialog.fill_warnings(warnings)
    checkDialog.fill_settings(setts)
    checkDialog.show()

    return checkDialog.exec_() 


    
  #  @QtCore.pyqtSlot(ImageChangePayload)
  def on_image_change_request(self, value):
    self.modify_image(self.full_image, value)

  #  @QtCore.pyqtSlot(ImageResizePayload)
  def on_image_resize_request(self, value):
    self.resize_image(self.full_image, value)


  #  @QtCore.pyqtSlot(str)
  def on_save_triggered(self, filename):
    try:
      self.full_image.save(filename)
    except:
      pass

  #  @QtCore.pyqtSlot(PatternPayload)
  def on_pattern_save_triggered(self, value):
    
    cont = self.pattern_checks()
    if not cont:
      return
    
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

    rect = painter.viewport()

    # Create key    
    # Use self.key which was filled last time image was changed
    
    tbl = QTableWidget()
    row = 0
    col = 0
    tbl.setColumnCount(15)
    tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
#    tbl.horizontalHeader().setStretchLastSection(True)

    tbl.horizontalHeader().hide()
    tbl.verticalHeader().hide()

    for item in self.key:
      tbl.setRowCount(row+1)
      
      tbl.setItem(row, col, QTableWidgetItem(item[4]))
      col = col + 1

      badgeMap = item[2].toqpixmap()
      badgeMap = badgeMap.scaled(50, 50, qtc.Qt.KeepAspectRatio, qtc.Qt.FastTransformation)
      tbl.setItem(row, col, QTableWidgetItem())
      widg = tbl.item(row, col)
      widg.setIcon(QIcon(badgeMap))

      col = col + 1

      symMap = item[3].toqpixmap()
      symMap = symMap.scaled(50, 50, qtc.Qt.KeepAspectRatio, qtc.Qt.FastTransformation)
      tbl.setItem(row, col, QTableWidgetItem())
      widg = tbl.item(row, col)
      widg.setIcon(QIcon(symMap))
      col = col + 1

      # Spare column between
      col = col + 1

      if col > 14:
        col = 0
        row = row + 1

    
    tbl_sz = tbl.size()
    print(tbl_sz, rect)
    
    tbl.setMaximumSize(tbl_sz)
    tbl.setMinimumSize(tbl_sz)
    
    out_scale = min(rect.width()/tbl_sz.width(), rect.height()/tbl_sz.height())*0.95
    print(out_scale)
    painter.scale(out_scale, out_scale)
    tbl.render(painter)
    # Handle descriptors

    
    painter.end()
    print("Pattern Complete")
    
    
def clearLayout(layout):
  # From https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt  or https://stackoverflow.com/a/10067548
  while layout.count():
    child = layout.takeAt(0)
    if child.widget():
      child.widget().deleteLater()
