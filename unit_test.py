import sys
import os

import cv2
import numpy

from filters import (
    apply_hdr_cpp,
    apply_hdr_bilateral_enhance,
    apply_gamma_enhance,
    apply_hdr_wls_enhance,
    apply_hdr_anisotropic_enhance,
)

# Add a tag to each function to shorten resulting photo names
TESTED_FUNCTIONS = [
    (apply_hdr_cpp, "cpp"),
    (apply_hdr_bilateral_enhance, "bil"),
    (apply_gamma_enhance, "gam"),
    (apply_hdr_wls_enhance, "wls"),
    (apply_hdr_anisotropic_enhance, "ani")
]
TEST_FOLDER = "unit_test_cpp"
ORIGINALS_FOLDER = "original"
RESULTS_FOLDER = "result"
VERIFICATION_FOLDER = "processed"

if __name__ == "__main__":
    if len(sys.argv) != 1:
        print(f"Usage: {sys.argv[0]}")

    for function in TESTED_FUNCTIONS:
        print(f"Testing function {function[0].__name__}...")
        for root, dirs, files in os.walk(os.path.join(TEST_FOLDER, ORIGINALS_FOLDER)):
            files.sort()
            nb_files_tested = len(files)
            for idx, name in enumerate(files):
                function[0](
                    os.path.join(root, name),
                    os.path.join(
                        TEST_FOLDER, RESULTS_FOLDER, f"res_{function[1]}_{idx}.jpg"
                    ),
                )

        for idx in range(nb_files_tested):
            print(f"Test {idx}:", flush=False)
            result = cv2.imread(
                os.path.join(
                    TEST_FOLDER, RESULTS_FOLDER, f"res_{function[1]}_{idx}.jpg"
                ), 0
            )
            verify = cv2.imread(
                os.path.join(
                    TEST_FOLDER, VERIFICATION_FOLDER, f"verif_{function[1]}_{idx}.jpg"
                ), 0
            )

            result = numpy.int32(result)
            verify = numpy.int32(result)
            difference = numpy.mean(result - verify)
            if abs(difference) > 100:
                print(f"LARGE DIFFERENCE! Mean difference: {difference}")
            elif abs(difference) > 0:
                print(f"Small difference! Mean difference: {difference}")
            else:
                print("OK")
