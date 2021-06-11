from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot
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

      #TODO This will always override - do only if changed?
      self.runner.set_pattern_name(self.output_file.text())
      
      self.runner.run_file(self.macro_file.text(), self.progressBar)

      self.imageH.full_image.show()
    
  @pyqtSlot()
  def macro_entered(self):

    input, output = self.runner.get_names(self.macro_file.text())
    if not self.input_file.text():
      self.input_file.setText(input)
    if not self.output_file.text():
      self.output_file.setText(output)


def main(args):

  app = QApplication(args)
  window = Ui()

  window.runner = MacroLoader()
  window.run_button.clicked.connect(window.run_pressed)

  window.imageH = ImageHandler(window, has_display=False)
  window.colourH = ColourOptionsHandler(window, has_display=False)

  window.runner.runner.image_change_request.connect( window.imageH.on_image_change_request)
  window.runner.runner.image_resize_request.connect( window.imageH.on_image_resize_request)
  window.runner.runner.pattern_save_request.connect( window.imageH.on_pattern_save_triggered)

  window.macro_file.editingFinished.connect(window.macro_entered)

  app.exec_()


if __name__ == "__main__":

  main(argv)