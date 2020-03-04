import os
import sys
from PIL import Image

LOW_RES = 800 * 600
MEDIUM_RES = 1280 * 720
HIGH_RES = 1920 * 1080


def create_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def main(src_folder, dest_folder):
    if not os.path.exists(f"./{src_folder}"):
        print(f"{src_folder} does not exist!")
    create_dir_if_not_exists(dest_folder)
    create_dir_if_not_exists(dest_folder + "/low-res")
    create_dir_if_not_exists(dest_folder + "/medium-res")
    create_dir_if_not_exists(dest_folder + "/high-res")
    create_dir_if_not_exists(dest_folder + "/ultra-res")

    for _, _, files in os.walk(src_folder):
        for image_file in files:
            try:
                image = Image.open(os.path.join(src_folder, image_file))
            except IOError as error:
                print(f"Error, {error}")
            width, height = image.size
            pixels = width * height
            if pixels <= LOW_RES:
                image.save(f"{dest_folder}/low-res/{image_file}")
            elif pixels <= MEDIUM_RES:
                image.save(f"{dest_folder}/medium-res/{image_file}")
            elif pixels <= HIGH_RES:
                image.save(f"{dest_folder}/high-res/{image_file}")
            else:
                image.save(f"{dest_folder}/ultra-res/{image_file}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python3 {sys.argv[0]} [src_folder] [dest_folder]")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
