import sys
import filters
import logger_setup
import structlog
import os

from scripts.collage_maker import collage_maker, CollageImage
from PIL import Image


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} source_img dest_folder")
        exit(1)
    _, source, dest = sys.argv

    logger_setup.setup()
    logger = structlog.get_logger()
    logger.info("Running script...")

    logger.info("Checking destination path...")
    if not os.path.exists(os.path.dirname(dest)):
        print("ERROR: Invalid destination path")
        logger.error("Invalid destination path")
        exit(1)
    logger.info("Destination path ok")

    logger.info("Verifying image path...")
    try:
        img = Image.open(source)
    except IOError:
        print("Source image path invalid")
        logger.error("Invalid image path")
        exit(1)
    logger.info("Image path ok")

    logger.info("Verifying format of source image...")
    if img.format not in ("JPEG", "JPG"):
        print("Only jpg/jpeg format images are accepted")
        logger.error("Image not in JPG format")
        exit(1)
    logger.info("Image format ok")

    collage_list = []

    logger.info("Running gamma enhance...")
    filters.apply_gamma_enhance(source, f"{dest}/gamma.jpg")
    collage_list.append(CollageImage(f"{dest}/gamma.jpg", "Gamma Enhancement"))
    logger.info("Gamma enhance applied successfully")

    logger.info("Running HDR WLS...")
    filters.apply_hdr_wls_enhance(source, f"{dest}/hdr-wls.jpg")
    collage_list.append(CollageImage(f"{dest}/hdr-wls.jpg", "HDR with WLS"))
    logger.info("HDR WLS applied successfully")

    logger.info("Running HDR Anisotropic...")
    filters.apply_hdr_anisotropic_enhance(source, f"{dest}/hdr-ani.jpg")
    collage_list.append(
        CollageImage(f"{dest}/hdr-ani.jpg", "HDR with Anisotropic Diffusion")
    )
    logger.info("HDR Anisotropic applied successfully")

    logger.info("Running HDR Bilateral...")
    filters.apply_hdr_bilateral_enhance(source, f"{dest}/hdr-bil.jpg")
    collage_list.append(
        CollageImage(f"{dest}/hdr-bil.jpg", "HDR with Bilateral Filter")
    )
    logger.info("HDR Bilateral applied successfully")

    logger.info("Generating collage...")
    collage_maker(collage_list, f"{dest}/comp.jpg")
    logger.info("Collage generated successfully")
