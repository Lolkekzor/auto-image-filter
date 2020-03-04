import sys
import subprocess
import logger_setup
from filters import apply_hdr_bilateral_enhance

logger_setup.setup()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} source_img dest_path [c/py]")
    _, source, dest, option = sys.argv

    if option == "py":
        apply_hdr_bilateral_enhance(source, dest)
    else:
        subprocess.call(["./cpp/DisplayImage", sys.argv[1], sys.argv[2]])
