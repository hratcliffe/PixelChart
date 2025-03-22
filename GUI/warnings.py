from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from importlib_resources import files

import re


class WarnDialog(QDialog):
  """Show a simple warning message and allow abort or continue
  Offers an option to request not to see this warning (caller to preserve if wished)
  """
  dialog_file = files('GUI').joinpath('WarningDialog.ui')

  def __init__(self):
    super(WarnDialog, self).__init__()
    loadUi(self.dialog_file, self)

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


class PresaveDialog(QDialog):
  """Show settings and warnings before saving/outputting a file
  Offers cancel or continue options
  """
  dialog_file = files('GUI').joinpath('PresaveDialog.ui')

  def __init__(self):
    super(PresaveDialog, self).__init__()
    loadUi(self.dialog_file, self)

  def fill_warnings(self, warnings_list):
    """Add each string in given list to Warnings section"""
    self.warn_layout = QVBoxLayout()
    self.warningsGroup.setLayout(self.warn_layout)

    for item in warnings_list:
      txt = QLabel(item)
      self.warn_layout.addWidget(txt)

  def fill_settings(self, settings_list):
    """Add each string in given list to Settings section"""

    self.set_layout = QVBoxLayout()
    self.settingsGroup.setLayout(self.set_layout)

    for item in settings_list:
      txt = QLabel(item)
      self.set_layout.addWidget(txt)

