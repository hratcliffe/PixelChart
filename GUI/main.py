from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi

from importlib_resources import files
from .file_handling import FileDetailsHandler, FileLoader
from .image_display import ImageHandler
from .colour_handling import ColourOptionsHandler
from Tracker.change_logger import ChangeLoggerQt

class Ui(QMainWindow):
  main_window_file = files('GUI').joinpath('Main.ui')

  def __init__(self):
    super(Ui, self).__init__()
    loadUi(self.main_window_file, self)
    self.show()

  # Fan out actions if needed
  def load_triggered(self, filename):
    self.imageH.show_image_from_file(filename)


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
  window.colourH.image_change_request.connect(window.tracker.store)
  window.fileH.image_resize_request.connect(window.tracker.store)
  window.fileL.save_triggered.connect(window.tracker.store)
  window.fileL.pattern_save_triggered.connect(window.tracker.store)
