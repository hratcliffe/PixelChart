from PyQt5.QtGui import QPixmap, QImage, QPainter, QFont, QIcon
from PyQt5.QtWidgets import QGraphicsView, QGridLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QProgressDialog
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
import PyQt5.QtCore as qtc
from PyQt5.QtCore import QSize, QRect

from PIL import ImageQt

from ColourHandling import *
from XStitchHeuristics import *

class PatternGenerator:
  """ Create a pattern output.
  This checks for validity of pattern to produce and warns of suspicious stuff
  (image too large, too many colours for sensible pattern)
  """
  def __init__(self):
    # Maximum size of image to consider "normal"
    self.max_sz = (200, 200)
    # Maximum number of colours to consider normal. Should be less than maximum number
    # of distinct symbols available for symbolic pattern
    self.max_colours = 50

    self.o_scl = 0.8

  def checks(self, details, im_sz, im_cols):
    """ Summarize pattern details and produce warnings for anything suspicious
    """

    warnings = []

    if im_sz[0] > self.max_sz[0] or im_sz[1] > self.max_sz[1]:
      warnings.append("Image size is very large ({} x {})".format(im_sz[0], im_sz[1]))

    if im_cols > self.max_colours:
      warnings.append("Number of colours is very large ({}). Symbolic pattern will have repeats!".format(im_cols))

    setts = []

    if details["Symbols"]:
      setts.append("Producing Symbolic Chart")
    if details["Key"]:
      setts.append("Producing Colour Key")
    if details["RGBCodes"] or details["ColourNumbers"]:
      tmp = "Producing Colour Ids: "
      if details["RGBCodes"]:
        tmp = tmp + "RGB codes "
      if details["ColourNumbers"]:
        tmp = tmp + "DMC Colour Approxes "
      setts.append(tmp)
    if details["FinalSize"]:
      setts.append("Producing Final Size at Gauge {}".format(details["Gauge"]))
    if details["LengthEstimates"]:
      setts.append("Producing Thread Length Estimates at Gauge {}".format(details["Gauge"]))

    if not setts:
      setts.append("No Settings To Report")

    if not warnings:
      warnings.append("No Warnings To Report")

    return {"settings":setts, "warnings":warnings}

  def rescale_to_page(self, pixmap, o_sz):
    """Rescale image ensuring pixelation retained"""
    sz = pixmap.size()
    sz.scale(o_sz, qtc.Qt.KeepAspectRatio)
    sz = sz*self.o_scl
    # Must scale pixmap manually to ensure transform is fast style, to retain pixelation
    return pixmap.scaled(sz.width()*self.o_scl, sz.height()*self.o_scl, qtc.Qt.KeepAspectRatio, qtc.Qt.FastTransformation)


  def get_size_text(self, im_sz, gg):
    """Create message summarizing piece pattern would create"""

    sz = estimateSize(im_sz, gg)
    mess = "{} by {} stitches, approx {}cm by {}cm at gauge {}".format(im_sz[0], im_sz[1], round(sz['cm'][0], 1), round(sz['cm'][1], 1), gg)
    return mess

  def make_key_table(self, do_codes, key):
    """Create a table for the colours in given key, including RGB codes if do_codes is set
    """

    if do_codes:
      #4 items, 2 sets, plus one padding
      col_cnt = 5+4
    else:
      # 3 items, 4 sets one padding
      col_cnt = 3*4 + 3

    tbl = QTableWidget()
    row = 0
    col = 0
    tbl.setColumnCount(col_cnt)
    tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    tbl.horizontalHeader().hide()
    tbl.verticalHeader().hide()

    for item in key:
      tbl.setRowCount(row+1)

      tbl.setItem(row, col, QTableWidgetItem(" ".join(item[4])))
      col = col + 1

      badgeMap = item[2].toqpixmap().scaled(50, 50, qtc.Qt.KeepAspectRatio, qtc.Qt.FastTransformation)
      tbl.setItem(row, col, QTableWidgetItem())
      tbl.item(row, col).setIcon(QIcon(badgeMap))

      col = col + 1

      symMap = item[3].toqpixmap().scaled(50, 50, qtc.Qt.KeepAspectRatio, qtc.Qt.FastTransformation)
      tbl.setItem(row, col, QTableWidgetItem())
      tbl.item(row, col).setIcon(QIcon(symMap))
      col = col + 1

      if do_codes:
        tbl.setItem(row, col, QTableWidgetItem(str(item[0])))
        col = col + 1
          
      col = col+1

      if col > col_cnt-1:
        col = 0
        row = row + 1
    
    tbl_sz = tbl.size()
    tbl.setMaximumSize(tbl_sz)
    tbl.setMinimumSize(tbl_sz)

    return tbl

  def make_colour_table(self, do_colours, do_lengths, image, key, cChart, gauge):
    """Create a table for the colours in given key, including colour names and
    estimates of length required if do_colours and do_lengths are true respectively.
    Colour names require a cChart mapping RGB codes to names
    Lengths requires the image (to count pixels) and a gauge selection (to size stitches)
    """

    col_per = 2
    if do_colours:
      col_per = col_per + 3
    elif do_lengths:
      col_per = col_per + 1

    col_cnt = col_per * 3 - 1

    tbl = QTableWidget()
    row = 0
    col = 0
    tbl.setColumnCount(col_cnt)
    tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    tbl.horizontalHeader().hide()
    tbl.verticalHeader().hide()

    for item in key:
      tbl.setRowCount(row+1)

      symMap = item[3].toqpixmap().scaled(50, 50, qtc.Qt.KeepAspectRatio, qtc.Qt.FastTransformation)
      tbl.setItem(row, col, QTableWidgetItem())
      tbl.item(row, col).setIcon(QIcon(symMap))
      col = col + 1

      if do_colours:
        r, g, b = item[0][0:3] #Ignore alpha if present
        colour = cChart.matchColour(colourItem(r, g, b))
        tbl.setItem(row, col, QTableWidgetItem(colour.name))
        col = col + 1
        tbl.setItem(row, col, QTableWidgetItem(colour.num))
        col = col + 1

        symMap = makeSwatch(colour.rgb).toqpixmap()
        symMap = symMap.scaled(50, 50, qtc.Qt.KeepAspectRatio, qtc.Qt.FastTransformation)
        tbl.setItem(row, col, QTableWidgetItem())
        tbl.item(row, col).setIcon(QIcon(symMap))
        col = col + 1

      if do_lengths:
        length = str(round(estimateLength(image, item[0], gauge), 1))+'m'
        tbl.setItem(row, col, QTableWidgetItem(length))
        col = col + 1

      col = col+1

      if col > col_cnt-1:
        col = 0
        row = row + 1

    tbl_sz = tbl.size()
    tbl.setMaximumSize(tbl_sz)
    tbl.setMinimumSize(tbl_sz)

    return tbl


  def save(self, filename, details, image, key, cChart):
    """Save a pattern file as PDF, with options as given in details dict"""

    progress = QProgressDialog("Saving Pattern", "Abort", 0, 4)
    progress.setWindowModality(qtc.Qt.WindowModal)
    progress.forceShow()

    printer = QPrinter(QPrinter.HighResolution)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(filename)

    painter = QPainter()
    painter.begin(printer)
    # Colour image

    rect = painter.viewport()
    o_sz = rect.size()

    # Draw title and header text
    painter.drawText(QRect(0, 0, o_sz.width(), o_sz.height()/40), qtc.Qt.AlignCenter, details["PTitle"])
    painter.drawText(QRect(0, o_sz.height()/40, o_sz.width(), o_sz.height()/20), qtc.Qt.AlignCenter, details["PText"])

    if details["FinalSize"]:
      mess = self.get_size_text(image.getImage(opt=False).size, details["Gauge"])
      painter.drawText(QRect(0, o_sz.height()/20, o_sz.width(), 3*o_sz.height()/40), qtc.Qt.AlignCenter, mess)

    # Colour image
    pixmap = self.rescale_to_page(image.getImage(opt=False).toqpixmap(), o_sz)
    rect.setSize(pixmap.size())
    # Move down. If landscape, will centre in width, portrait will centre in height. Other dimension will still fit
    painter.translate(o_sz.width()*(1-self.o_scl)/2, o_sz.height()*(1-self.o_scl)/2)
    painter.drawPixmap(rect, pixmap)

    progress.setValue(1)

    if details["Symbols"] and not progress.wasCanceled():
      printer.newPage()

      # Symbolic image
      pixmap = self.rescale_to_page(toSymbolicImage(image).getImage(opt=False).toqpixmap(), o_sz)
      rect.setSize(pixmap.size())
      painter.drawPixmap(rect, pixmap)
    
    progress.setValue(2)

    if details["Key"] or details["ColourNumbers"] or details["LengthEstimates"]:
      printer.newPage()

    # Create key    
    if details["Key"] and not progress.wasCanceled():
    
      tbl = self.make_key_table(details["RGBCodes"], key)
      tbl_sz = tbl.size()
    
      out_scale = min(rect.width()/tbl_sz.width(), rect.height()/tbl_sz.height())*0.95
      painter.scale(out_scale, out_scale)
      tbl.render(painter)

    progress.setValue(3)
    
    # Handle descriptors
    
    # Reprint key without names, but with codes (if requested) and lengths (if requested). Only do this if one of those options was requested
    if (details["ColourNumbers"] or details["LengthEstimates"]) and not progress.wasCanceled():
    
      tbl = self.make_colour_table(details["ColourNumbers"], details["LengthEstimates"], image, key, cChart, details["Gauge"])
      tbl_sz = tbl.size()
      # Move down below previous table. 
      painter.translate(0, tbl_sz.height())
      tbl.render(painter)

    progress.setValue(4)

    
    painter.end()
    print("Pattern Complete")
    
