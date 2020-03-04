import os

from PIL import Image, ImageDraw, ImageFont


class CollageImage:
    def __init__(self, path, tag=""):
        self.path = path
        self.tag = tag


def collage_maker(tagged_images, resulting_path):
    """
    Helper function that takes in an array of CollageImages.
    Creates a collage of those images at the resulting_path given.
    """

    images_nb = len(tagged_images)
    if images_nb == 0:
        print("No images to compose")
        return None

    if not os.path.exists(os.path.dirname(resulting_path)):
        print("Invalid collage result path")
        return None

    max_width, max_height = (
        max(Image.open(image.path).size[0] for image in tagged_images),
        max(Image.open(image.path).size[1] for image in tagged_images),
    )

    rows = (images_nb - 1) // 2 + 1
    composed_image = Image.new("RGB", (max_width * 2, max_height * rows))

    for idx, image in enumerate(tagged_images):
        with Image.open(image.path) as opened_image:

            font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 35)
            overlay = ImageDraw.Draw(opened_image)
            overlay.text((10, 10), image.tag, fill=(0, 255, 255), font=font)

            composed_image.paste(
                opened_image,
                (0 if idx % 2 == 0 else max_width, max_height * (idx // 2)),
            )

    composed_image.save(resulting_path)
