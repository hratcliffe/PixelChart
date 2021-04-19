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
    
    pixmap = self.full_image.getImage(opt=False).toqpixmap()
    sz = pixmap.size()
    sz_b = pixmap.size()
    port_sz = self.pane.viewport().size()
    sz.scale(port_sz, qtc.Qt.KeepAspectRatio)
    scl = 0.95  #Scale down slightly to accomodate borders and things
    pixmap = pixmap.scaled(sz.width()*scl, sz.height()*scl, qtc.Qt.KeepAspectRatio, qtc.Qt.FastTransformation)

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
    
    # Factor to reduce image size relative to page
    scl = 0.8
    
    filename = value.filename
            
    printer = QPrinter(QPrinter.HighResolution)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(filename)
    
    painter = QPainter()
    painter.begin(printer)
    # Colour image
    
    rect = painter.viewport()
    o_sz = rect.size()
            
    pixmap = self.full_image.getImage(opt=False).toqpixmap()
    sz = pixmap.size()
    sz.scale(o_sz, qtc.Qt.KeepAspectRatio)
    sz = sz*scl
    # Must scale pixmap manually to ensure transform is fast style, to retain pixelation
    pixmap = pixmap.scaled(sz.width()*scl, sz.height()*scl, qtc.Qt.KeepAspectRatio, qtc.Qt.FastTransformation)

    rect.setSize(sz)
    # Move down. If landscape, will centre in width, portrait will centre in height. Other dimension will still fit
    painter.translate(o_sz.width()*(1-scl)/2, o_sz.height()*(1-scl)/2)
    painter.drawPixmap(rect, pixmap)
    
    printer.newPage()

    # Symbolic image
    pixmap = toSymbolicImage(self.full_image).getImage(opt=False).toqpixmap()
    sz = pixmap.size()
    sz.scale(o_sz, qtc.Qt.KeepAspectRatio)
    sz = sz*scl
    # Must scale pixmap manually to ensure transform is fast style, to retain pixelation
    pixmap = pixmap.scaled(sz.width()*scl, sz.height()*scl, qtc.Qt.KeepAspectRatio, qtc.Qt.FastTransformation)

    rect.setSize(sz)
    painter.drawPixmap(rect, pixmap)
    
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
      
      tbl.setItem(row, col, QTableWidgetItem(" ".join(item[4])))
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
