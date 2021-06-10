from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal

from importlib_resources import files

from SharedData.types import ImageLoadPayload
from .file_handling import FileDetailsHandler, FileLoader
from .image_display import ImageHandler
from .colour_handling import ColourOptionsHandler
from Tracker.change_logger import ChangeLoggerQt

class Ui(QMainWindow):
  main_window_file = files('GUI').joinpath('Main.ui')
  load_triggered_sig = pyqtSignal(ImageLoadPayload, name="load_triggered")


  def __init__(self):
    super(Ui, self).__init__()
    loadUi(self.main_window_file, self)
    self.show()

  # Fan out actions if needed
  def load_triggered(self, filename):
    self.imageH.show_image_from_file(filename)
    self.load_triggered_sig.emit(ImageLoadPayload(filename))


def run_app(args):
  app = QApplication(args)
  window = Ui()

  window.fileH = FileDetailsHandler(window)
  window.fileL = FileLoader(window, window.fileH)
  window.imageH = ImageHandler(window)
  window.colourH = ColourOptionsHandler(window)

  window.tracker = ChangeLoggerQt()

  cross_connect(window)

  app.exec_() # Start the application


def cross_connect(window):

  window.imageH.image_changed.connect(window.fileH.on_image_changed)   
  window.imageH.image_changed.connect(window.colourH.on_image_changed)
  
  window.colourH.image_change_request.connect( window.imageH.on_image_change_request)

  window.fileH.image_resize_request.connect( window.imageH.on_image_resize_request)

  window.fileL.save_triggered.connect(window.imageH.on_save_triggered)
  window.fileL.pattern_save_triggered.connect(window.imageH.on_pattern_save_triggered)

  # Connect up all necessary global ops. to tracker
  # NOTE this is not ALL tracker connections!
  # Temporary objects might have additional connections where created
  window.load_triggered_sig.connect(window.tracker.store)
  window.colourH.image_change_request.connect(window.tracker.store)
  window.fileH.image_resize_request.connect(window.tracker.store)
  window.fileL.save_triggered.connect(window.tracker.store)
  window.fileL.pattern_save_triggered.connect(window.tracker.store)
