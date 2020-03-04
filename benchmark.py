import sys

from filters import (
    apply_gamma_enhance,
    apply_hdr_wls_enhance,
    apply_hdr_anisotropic_enhance,
    apply_hdr_bilateral_enhance,
    apply_hdr_cpp
)
from benchmark_report import BenchmarkReport


class BenchmarkFunction:
    def __init__(self, function, tag):
        self.function = function
        self.tag = tag


def main(source_folder="benchmark_images", dest_folder="benchmark_results"):
    """
    The arguments are:
    source_folder - where the test_sets folders must be
    dest_folder - path where the resulting images will be created

    The test_sets and benchmark_functions arrays must be set below
    The functions must take in a path as the source image and a
    path as the destination where the processed image will be created
    """
    test_sets = ["high_res", "medium_res", "low_res"]
    benchmark_functions = [
        # BenchmarkFunction(apply_gamma_enhance, "gamma"),
        # BenchmarkFunction(apply_hdr_wls_enhance, "hdr_wls"),
        # BenchmarkFunction(apply_hdr_anisotropic_enhance, "hdr_adiff"),
        # BenchmarkFunction(apply_hdr_bilateral_enhance, "hdr_bilat"),
        BenchmarkFunction(apply_hdr_cpp, "hdr_cpp")
    ]

    benchmark = BenchmarkReport(
        source_folder, dest_folder, test_sets, benchmark_functions
    )
    benchmark.setup()
    benchmark.run_benchmark()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        main()
