from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi

from importlib_resources import files
from .file_handling import FileDetailsHandler, FileLoader
from .image_display import ImageHandler
from .colour_handling import ColourOptionsHandler

# Main window. Contains 4 main elements
class Ui(QMainWindow):
  main_window_file = files('GUI').joinpath('Main.ui')

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

    # Setup connections between the main elements
    self.cross_connect()

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

  # Fan out actions if needed
  def load_triggered(self, filename):
    self.imageH.show_image_from_file(filename)


def run_app(args):
  app = QApplication(args)
  window = Ui()
  app.exec() # Start the application

