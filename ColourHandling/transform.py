# Module handling transforms of images such as brightness changes
from . import imageExt
from PIL import ImageEnhance

def modifyBrightness(image, val):
    """Modify given image to change its brightness.
    Image should be a PIL image.
    New brightness is relative to 1 (< 1 darkens, >1 brightens)
    """
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(val)

def modifyContrast(image, val):
    """Modify given image to change its contrast.
    Image should be a PIL image.
    New contrast is relative to 1 (< 1 lowers, >1 increases)
    """
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(val)

def modifySaturation(image, val):
    """Modify given image to change its saturation.
    Image should be a PIL image.
    New saturation is relative to 1 (< 1 lowers, >1 increases)
    """
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(val)


