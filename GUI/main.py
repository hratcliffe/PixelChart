from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from importlib_resources import files
from .file_handling import FileDetailsHandler, FileLoader
from .image_display import ImageHandler
from .types import *

import sys

class Ui(QMainWindow):
  main_window_file = files('GUI').joinpath('Main.ui')

  def __init__(self):
    super(Ui, self).__init__() # Call the inherited classes __init__ method
    uic.loadUi(self.main_window_file, self) # Load the .ui file
    self.show() # Show the GUI

  # Fan out actions
  def load_triggered(self, filename):
    self.imageH.change_image(filename)


def run_app(args):
  app = QApplication(args) # Create an instance of QtWidgets.QApplication
  window = Ui() # Create an instance of our class

  window.fileH = FileDetailsHandler(window)
  window.fileL = FileLoader(window, window.fileH)
  window.imageH = ImageHandler(window)

  cross_connect(window)

  app.exec_() # Start the application


def cross_connect(window):

  window.imageH.image_changed.connect(window.fileH.on_image_changed)