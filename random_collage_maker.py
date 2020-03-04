import sys
import random
import os

from scripts.collage_maker import CollageImage, collage_maker
import filters

AUX_FOLDER = "aux_folder"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} source_folder dest_folder")
        exit(1)
    _, source_directory, destination_directory = sys.argv

    correspondence_text = ["original", "gamma", "bil", "wls"]

    correspondence_file = open("corrsep.txt", "w+")

    directory = os.fsencode(source_directory)
    # For each test set, iterate through all images (files)
    for idx, fileraw in enumerate(os.listdir(directory)):
        collage_images = []
        paths = [
            ["", 0],
            [os.path.join(AUX_FOLDER, f"gma{idx:02}.jpg"), 1],
            [os.path.join(AUX_FOLDER, f"bil{idx:02}.jpg"), 2],
            [os.path.join(AUX_FOLDER, f"wls{idx:02}.jpg"), 3],
        ]

        filename = os.fsdecode(fileraw)
        filters.apply_gamma_enhance(
            os.path.join(source_directory, filename),
            os.path.join(AUX_FOLDER, f"gma{idx:02}.jpg"),
        )
        filters.apply_hdr_bilateral_enhance(
            os.path.join(source_directory, filename),
            os.path.join(AUX_FOLDER, f"bil{idx:02}.jpg"),
        )
        filters.apply_hdr_wls_enhance(
            os.path.join(source_directory, filename),
            os.path.join(AUX_FOLDER, f"wls{idx:02}.jpg"),
        )

        paths[0][0] = os.path.join(source_directory, filename)
        shuffled_paths = random.shuffle(paths)

        for path_idx, path in enumerate(paths):
            print(path[1])
            collage_images.append(CollageImage(path[0], f"{path_idx + 1}"))
            correspondence_file.write(
                f"{path_idx + 1} -> {correspondence_text[path[1]]} ; "
            )
        correspondence_file.write(f"collage{idx:02}\n")

        collage_maker(collage_images, f"survey/collage{idx:02}.jpg")
