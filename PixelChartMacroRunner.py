from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
#Is QT application to use signalling system as the rest of the code does
# This allows GUI for filename input and progress tracker etc

from sys import argv
from importlib_resources import files

from Tracker.macro_system import MacroLoader
from GUI.image_display import ImageHandler
from GUI.colour_handling import ColourOptionsHandler


class Ui(QMainWindow):
  main_window_file = files('Tracker').joinpath('Main.ui')

  def __init__(self):
    super(Ui, self).__init__()
    loadUi(self.main_window_file, self)
    self.show()

  def run_pressed(self):
  
    if self.runner:
      self.imageH.show_image_from_file(self.input_file.text())
      self.runner.run_file(self.macro_file.text(), showProgress=self.progress_check)

    self.imageH.full_image.show()

def main(args):

  app = QApplication(args)
  window = Ui()

  window.runner = MacroLoader()
#  window.runner.run_file("test.json")
  window.run_button.clicked.connect(window.run_pressed)

  window.imageH = ImageHandler(window, has_display=False)
  window.colourH = ColourOptionsHandler(window, has_display=False)

  window.runner.runner.image_change_request.connect( window.imageH.on_image_change_request)
  window.runner.runner.image_resize_request.connect( window.imageH.on_image_resize_request)


  app.exec_()


if __name__ == "__main__":

  main(argv)