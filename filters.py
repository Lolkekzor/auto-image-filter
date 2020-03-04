import subprocess
import structlog
import cv2

from PIL import Image
from gamma_filter import process_image
from hdr_enhance.hdr import FakeHDR


def cv_open(image_path):
    try:
        return cv2.imread(image_path, -1)
    except OSError:
        structlog.get_logger().error(f"Image path invalid, {OSError}")


def pil_open(image_path):
    try:
        return Image.open(image_path)
    except OSError:
        structlog.get_logger().error(f"Image path invalid, {OSError}")


def apply_gamma_enhance(source_path, dest_path):
    process_image(pil_open(source_path)).save(dest_path)


def apply_hdr_wls_enhance(source_path, dest_path):
    hdr_image = FakeHDR(True).process(cv_open(source_path))
    cv2.imwrite(dest_path, 255 * hdr_image)


def apply_hdr_anisotropic_enhance(source_path, dest_path):
    hdr_image = FakeHDR(True).process(cv_open(source_path), True)
    cv2.imwrite(dest_path, 255 * hdr_image)


def apply_hdr_bilateral_enhance(source_path, dest_path):
    hdr_image = FakeHDR(True).process(cv_open(source_path), False, True)
    cv2.imwrite(dest_path, 255 * hdr_image)


def apply_hdr_cpp(source_path, dest_path):
    PATH_TO_CPP_OBJECT = "./cpp/hdr"
    ret_code = subprocess.call([PATH_TO_CPP_OBJECT, source_path, dest_path])
    if ret_code != 0:
        structlog.get_logger().error(f"HDR Cpp failed")
