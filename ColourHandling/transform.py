from . import imageExt
from PIL import ImageEnhance

def modifyBrightness(image, val):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(val)

def modifyContrast(image, val):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(val)

def modifySaturation(image, val):
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(val)


