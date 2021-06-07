from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
#Is QT application to use signalling system as the rest of the code does
# This allows GUI for filename input and progress tracker etc

from sys import argv

from Tracker.macro_system import MacroLoader

def main(args):

  app = QApplication(args)
  #TODO Create window here once we have created UI

  runner = MacroLoader()
  runner.run_file("test.json")


if __name__ == "__main__":

  main(argv)