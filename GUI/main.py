from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.uic import loadUi
from PyQt6.QtCore import pyqtSignal

from importlib_resources import files

from SharedData.types import ImageLoadPayload
from .file_handling import FileDetailsHandler, FileLoader
from .image_display import ImageHandler
from .colour_handling import ColourOptionsHandler
from Tracker.change_logger import ChangeLoggerQt

# Main window. Contains 4 main elements
class Ui(QMainWindow):
  main_window_file = files('GUI').joinpath('Main.ui')
  load_triggered_sig = pyqtSignal(ImageLoadPayload, name="load_triggered")


  def __init__(self):
    super(Ui, self).__init__()
    loadUi(self.main_window_file, self)

    # Handles details of filename and selections for pattern output
    self.fileH = FileDetailsHandler(self)
    # Handles file loading
    self.fileL = FileLoader(self, self.fileH)
    # Handles Image display and modification
    self.imageH = ImageHandler(self)
    # Handles toolbar showing colour adjustments
    self.colourH = ColourOptionsHandler(self)

    self.tracker = ChangeLoggerQt()

    # Setup connections between the main elements
    self.cross_connect()

    self.tracker.start()

    self.show()

  def cross_connect(self):
    """Connect the sub-elements of the window together using signals"""

    # Actions to take when image is modified
    self.imageH.image_changed.connect(self.fileH.on_image_changed)
    self.imageH.image_changed.connect(self.colourH.on_image_changed)

    # Actions that colour options input can precipitate
    self.colourH.image_change_request.connect( self.imageH.on_image_change_request)
    self.colourH.image_enhance_request.connect( self.imageH.on_image_enhance_request)
    self.colourH.image_combine_request.connect( self.imageH.on_image_combine_request)

    # Actions that file options can precipitate
    self.fileH.image_resize_request.connect( self.imageH.on_image_resize_request)

    # Actions that file loader can precipitate
    self.fileL.save_triggered.connect(self.imageH.on_save_triggered)
    self.fileL.pattern_save_triggered.connect(self.imageH.on_pattern_save_triggered)


    # Connect up all necessary global ops. to tracker
    # NOTE this is not ALL tracker connections!
    # Temporary objects might have additional connections where created
    self.load_triggered_sig.connect(self.tracker.store)
    self.colourH.image_change_request.connect(self.tracker.store)
    self.fileH.image_resize_request.connect(self.tracker.store)
    self.fileL.save_triggered.connect(self.tracker.store)
    self.fileL.pattern_save_triggered.connect(self.tracker.store)


  # Fan out actions if needed
  def load_triggered(self, filename):
    self.imageH.show_image_from_file(filename)
    self.load_triggered_sig.emit(ImageLoadPayload(filename))


def run_app(args):
  app = QApplication(args)
  window = Ui()
  app.exec() # Start the application

  # test code
  window.tracker.write("test.json")

