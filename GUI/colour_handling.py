from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from .types import ImageStatePayload, ImageChangePayload, ImageCombinePayload, ImageEnhancePayload
from XStitchHeuristics.colours import listBrands
from .recolour import CombinerDialog

_default_reduce_number = 20
_default_enhance_base = 100
_default_enhance_step = 0.1

class ColourOptionsHandler(QObject):
  """ Handle GUI function relating to image colouring
  """
  image_change_request = pyqtSignal(ImageChangePayload, name="image_change_request")
  image_enhance_request = pyqtSignal(ImageEnhancePayload, name="image_enhance_request")
  image_combine_request = pyqtSignal(ImageCombinePayload, name="image_combine_request")

  def __init__(self, window):
    super(ColourOptionsHandler, self).__init__()

    self.window = window

    fill_colour_combos(window)

    # Go button applies selected options
    self.go_button = window.colour_go_button
    self.go_button.clicked.connect(self.go_button_clicked)

    # Brightness/contrast/saturation up/down buttons handled separately
    window.brightDown.clicked.connect(self.br_down)
    window.brightUp.clicked.connect(self.br_up)

    window.contDown.clicked.connect(self.co_down)
    window.contUp.clicked.connect(self.co_up)

    window.satDown.clicked.connect(self.sat_down)
    window.satUp.clicked.connect(self.sat_up)

    # Advanced button opens new dialog
    self.adv_button = window.colour_advanced_button
    self.adv_button.clicked.connect(self.adv_button_clicked)

  def set_num_colours(self, num):
    """Populate window with count of colours in image (num) and
    populate drop-down for colour reduction with suggested choice
    """

    # Shows current number and caps reduction at this
    self.window.current_cols.setText(str(num))
    self.window.colour_num_select.setMaximum(num)

    # Set suggested number to reduce to, at most current count
    if num > _default_reduce_number:
      self.window.colour_num_select.setValue(_default_reduce_number)
    else:
      self.window.colour_num_select.setValue(num)


  def go_button_clicked(self):
    """ Apply selected options (emit signal)
    """
    # Extract colour options
    num = self.window.colour_num_select.value()

    vals = {"Emphasize": self.window.emphasize_select.currentData(), "Optimize": self.window.optimize_select.currentData(), "Palette":self.window.palette_select.currentData()}

    self.image_change_request.emit(ImageChangePayload(num, opts=vals))

  def br_change(self, val):
    # Emit request to change brightness
    oldval = _default_enhance_base
    newval = oldval*(1 + _default_enhance_step*val)
    self.image_enhance_request.emit(ImageEnhancePayload("br", oldval, newval))

  def br_down(self):
    self.br_change(-1)
  def br_up(self):
    self.br_change(1)

  def co_change(self, val):
    # Emit request to change contrast
    oldval = _default_enhance_base
    newval = oldval*(1 + _default_enhance_step*val)
    self.image_enhance_request.emit(ImageEnhancePayload("co", oldval, newval))
  def co_down(self):
    self.co_change(-1)
  def co_up(self):
    self.co_change(1)

  def sat_change(self, val):
    # Emit request to change saturation
    oldval = _default_enhance_base
    newval = oldval*(1 + _default_enhance_step*val)
    self.image_enhance_request.emit(ImageEnhancePayload("sat", oldval, newval))
  def sat_down(self):
    self.sat_change(-1)
  def sat_up(self):
    self.sat_change(1)

  def combine_triggered(self, payload):
    self.image_combine_request.emit(payload)

  def adv_button_clicked(self):
    """ Start Advanced options dialog procedure
    If no image is loaded, this is a No-op
    """

    if(not self.window.imageH.check_for_image()):
      return

    #Temporary - just start colour picker
    advDialog = CombinerDialog(self.window.imageH.get_image(), self.combine_triggered)
    advDialog.exec()

  # Apply any GUI updates needed when image state changes
  @pyqtSlot(ImageStatePayload)
  def on_image_changed(self, value):
    self.set_num_colours(value.n_cols)


def fill_colour_combos(window):
  """ Populate combo boxes with image options
  """

  window.emphasize_select.addItem("None", '0')
  window.emphasize_select.addItem("Red", 'r')
  window.emphasize_select.addItem("Blue", 'b')
  window.emphasize_select.addItem("Green", 'g')
  window.emphasize_select.addItem("Lines", 'l')
  window.emphasize_select.addItem("Brights", 'h')
  window.emphasize_select.addItem("Shade", 's')

  window.optimize_select.addItem("None", '0')
  window.optimize_select.addItem("Landscape", 'l')
  window.optimize_select.addItem("Portrait", 'p')
  window.optimize_select.addItem("Object", 'o')

  brands = listBrands()
  window.palette_select.addItem("None", None)
  for item in brands:
    window.palette_select.addItem(item[0], item[1])

