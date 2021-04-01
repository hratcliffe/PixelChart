from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
from importlib_resources import files

import re


class WarnDialog(QDialog):
  dialog_file = files('GUI').joinpath('WarningDialog.ui')

  def __init__(self):
    super(WarnDialog, self).__init__() # Call the inherited classes __init__ method
    uic.loadUi(self.dialog_file, self) # Load the .ui file
        
  def set_message(self, message):
    self.message.setText(message)

  def set_options(self, adjust, ignore):
    self.continueAdjust.setText(_subs(self.continueAdjust.text(), adjust))
    self.continueRetain.setText(_subs(self.continueRetain.text(), ignore))
    
  def check_dontAskState(self):
    return self.dontAsk.isChecked()
    
    
def _subs(text, sub):
  # Substitue sub into text where FIRST <> are found. If there are more than one pair, can call repeatedly and will subs from left to right
  res = re.match(r"(.*)<.*>(.*)", text)
  new_str = [res.group(1), sub, res.group(2)]
  
  return ''.join(new_str)
  
  