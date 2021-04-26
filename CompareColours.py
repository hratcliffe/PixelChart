from GUI import *

from PyQt5.QtWidgets import QMainWindow, QApplication

from sys import argv


if __name__ == "__main__":

  app = QApplication(argv) # Create an instance of QtWidgets.QApplication

  window = QMainWindow()
  window.setCentralWidget(ColourComparator())

  window.show()

  app.exec_()

