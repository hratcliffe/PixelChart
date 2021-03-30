from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from importlib_resources import files
from .file_handling import FileHandler

import sys

class Ui(QMainWindow):
  main_window_file = files('GUI').joinpath('Main.ui')

  def __init__(self):
    super(Ui, self).__init__() # Call the inherited classes __init__ method
    uic.loadUi(self.main_window_file, self) # Load the .ui file
    self.show() # Show the GUI


def run_app(args):
  app = QApplication(args) # Create an instance of QtWidgets.QApplication
  window = Ui() # Create an instance of our class

  fileH = FileHandler(window)

  app.exec_() # Start the application
