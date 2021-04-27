from PyQt5.QtWidgets import QDialog, QLabel, QGridLayout, QPushButton

from .colour_comparator import ColourComparator

class RecolourDialog(QDialog):

  def __init__(self, palette):
    super(RecolourDialog, self).__init__() 
    
    self.palette = palette
    self.pickerWidget = ColourComparator(chart=palette)
    
    self.layout = QGridLayout()
    self.layout.addWidget(self.pickerWidget, 0, 0)
    
    self.skip_butt = QPushButton()
    self.skip_butt.setText("Skip and Next")
    self.layout.addWidget(self.skip_butt, 1, 1)

    self.next_butt = QPushButton()
    self.next_butt.setText("Accept and Next")
    self.layout.addWidget(self.next_butt, 1, 2)
        
    self.setLayout(self.layout)

    # Why aren't these buttons showing up???
    
  def do_recolour(self, image):

    self.exec_()  
    
