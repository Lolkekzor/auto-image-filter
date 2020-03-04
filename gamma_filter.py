import numpy as np
from PIL import Image, ImageOps, ImageStat

BRIGHTNESS_THRESHOLD = 127.5


def gamma_correction(image, gamma):
    """
    Splits image into RGB channels, then applies point-wise
    correction based on gamma parameter

    Returns: Gamma-corrected image
    """
    source = image.split()
    source = [x.point(lambda p: ((p / 255.0) ** gamma) * 255) for x in source]
    return Image.merge(image.mode, source)


def compute_average_brightness(image):
    """
    Computes average brightness of the grayscale version of an image

    Returns: Float from 0 to 255
    """
    source = ImageOps.grayscale(image)
    return ImageStat.Stat(source)._getmean()[0]


def compute_automatic_gamma(image, light_bias=True):
    """
    Computes automatic gamma correction value to shift brightness histogram
    of a photo to have a mean value of 1/2.
    If light_bias is true, this is skewed to not modify brighter photos.
    A bright photo will not be darkened too much.

    Returns: A float representing the gamma correction value
    """
    avg_brightness = compute_average_brightness(image)
    if light_bias and avg_brightness > BRIGHTNESS_THRESHOLD:
        avg_brightness = (
            BRIGHTNESS_THRESHOLD + (avg_brightness - BRIGHTNESS_THRESHOLD) / 4
        )
    return -0.3 / np.log10(avg_brightness / 255.0)


def process_image(img):
    return gamma_correction(img, compute_automatic_gamma(img))
