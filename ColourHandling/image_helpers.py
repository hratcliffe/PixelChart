# Module handling some extra image stuff such as space transforms
from PIL import ImageCms

# Handles image mode conversion for PIL images
# Use for transforms that need building so that
# we can stash them for repeated use

class imageModeHelper:

  transform_registry = {}

  def __init__(self):
    pass

  def cache(self, name, trans):
    self.transform_registry[name] = trans
    
  def get(self, name):
    return self.transform_registry[name]

  def _transform_key(self, init, final):
    # Create the string key for registry from init and final profile names
    
    return init+'_'+final
    
  def changeMode(self, image, init, final):

    # Note : "["LAB", "XYZ", "sRGB"]" are available colour spaces"
    request = self._transform_key(init, final)
    
    try:
      transform = self.get(request)
    except:
      # Build transform
      if init == "RGB":
        init_profile = ImageCms.createProfile("sRGB")
      else:
        init_profile = ImageCms.createProfile(init)

      if final == "RGB":
        final_profile = ImageCms.createProfile("sRGB")
      else:
        final_profile  = ImageCms.createProfile(final)

      transform = ImageCms.buildTransformFromOpenProfiles(init_profile, final_profile, init, final)

      self.cache(request, transform)

    return ImageCms.applyTransform(image, transform)

