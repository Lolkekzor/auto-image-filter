import time
import functools
import os

from statistics import mean
from shutil import rmtree


def time_function(func, benchmark_writer):
    """
    Decorator used to time functions
    """

    @functools.wraps(func)
    def timed_function(*args, **kwargs):
        start_time = time.perf_counter()
        return_value = func(*args, **kwargs)
        end_time = time.perf_counter()

        benchmark_writer.log_execution_time(end_time - start_time)

        return return_value

    return timed_function


class BenchmarkReport:
    """
    This class is used to set up and run a benchmark for a given list of image enhancing functions
    source_folder = folder where the test sets reside, each with a set of images
    dest_folder = folder where the resulting images will be produced
    test_sets = the sets in which the input images are partitioned
    test_functions = the functions to be benchmarked, each with an associated tag (name) to display
    """

    def __init__(self, source_folder, dest_folder, test_sets, test_functions):
        self.execution_times = {}
        self.image_sizes = {}
        self.current_function = None
        self.current_test_set = None
        self.source_folder = source_folder
        self.dest_folder = dest_folder
        self.test_sets = test_sets
        # Apply decorator to test functions, and get tags for display
        self.test_functions = [
            time_function(x.function, benchmark_writer=self) for x in test_functions
        ]
        self.function_tags = [x.tag for x in test_functions]

        self.tested_functions_count = len(self.test_functions)
        self.test_sets_count = len(self.test_sets)

        self.initialized = False

    def log_execution_time(self, time):
        """
        Adds a time entry to the execution_times dictionary as following:
        execution_times[function][test_set].append(time)
        For each function and test set we have an array of time logs
        """
        if self.current_function not in self.execution_times:
            self.execution_times[self.current_function] = {}
        if self.current_test_set not in self.execution_times[self.current_function]:
            self.execution_times[self.current_function][self.current_test_set] = []
        self.execution_times[self.current_function][self.current_test_set].append(time)

    def log_image_size(self, size):
        """
        Adds a size entry to the image_sizes dictionary as following:
        image_sizes[function][test_set] = size
        For each function and test set we have the size increase (as a percentage)
        """
        if self.current_function not in self.image_sizes:
            self.image_sizes[self.current_function] = {}
        self.image_sizes[self.current_function][self.current_test_set] = size

    @staticmethod
    def compute_percent_ratio(original_sizes_average, processed_sizes_average):
        try:
            return processed_sizes_average / original_sizes_average * 100
        except ZeroDivisionError:
            print("ERROR: Division by zero")
            exit(1)

    def setup(self):
        if None in (self.test_sets, self.test_functions, self.dest_folder):
            print("Invalid benchmark initialization")
            exit(1)

        if not os.path.exists(self.source_folder):
            print(
                "ERROR: Benchmark folder does not exist!\
                Please enter a valid path"
            )
            exit(1)
        for test_set in self.test_sets:
            if not os.path.exists(os.path.join(self.source_folder, test_set)):
                print("ERROR: Test set folder '{test_set}' does not exist!")
                exit(1)

        if os.path.exists(self.dest_folder):
            print(
                "Results directory already exists, do you want to remove it and redo benchmark? (Y/N)"
            )
            if input().upper() in ["Y", "YES"]:
                rmtree(self.dest_folder)
            else:
                print("Aborting benchmark. Results were not deleted.")
                exit(1)
        os.makedirs(self.dest_folder)
        for test_set in self.test_sets:
            os.makedirs(os.path.join(self.dest_folder, test_set))

        self.initialized = True

    def run_benchmark(self):
        if self.initialized is False:
            raise Exception(
                "Benchmark was not initialized! .setup() must be called before .run_benchmark()"
            )
        # Iterate through all functions that need to be benchmarked
        for func_idx, current_benchmark in enumerate(self.test_functions):
            # Inform logger about what function is currently being run
            self.current_function = self.function_tags[func_idx]
            # For each function, iterate through all test sets (folders)
            for test_set in self.test_sets:
                size_original = 0
                size_enhanced = 0
                # Inform logger about what test set is currently being run
                self.current_test_set = test_set
                directory = os.fsencode(os.path.join(self.source_folder, test_set))
                # For each test set, iterate through all images (files)
                for idx, fileraw in enumerate(os.listdir(directory)):
                    filename = os.fsdecode(fileraw)
                    source_image_path = os.path.join(
                        self.source_folder, test_set, filename
                    )
                    destination_image_path = os.path.join(
                        self.dest_folder,
                        test_set,
                        f"{idx:03}-{self.function_tags[func_idx]}.jpg",
                    )

                    # Run function on current image
                    current_benchmark(source_image_path, destination_image_path)
                    print(f"{self.function_tags[func_idx]}: {source_image_path}")
                    size_original += os.path.getsize(source_image_path)
                    size_enhanced += os.path.getsize(destination_image_path)

                self.log_image_size(
                    BenchmarkReport.compute_percent_ratio(
                        size_original / len(os.listdir(directory)),
                        size_enhanced / len(os.listdir(directory)),
                    )
                )

        self.generate()

    @staticmethod
    def open_results_file():
        return open("results.md", "w+")

    def write_header(self, results_file):
        results_file.write("# Benchmark results\n\n")
        results_file.write(
            f"## Number of tested algorithms:{self.tested_functions_count}\n"
        )
        results_file.write(f"## Number of test sets: {self.test_sets_count}\n\n")
        results_file.write("Test set 1: Low resolution\n\n")
        results_file.write("Test set 2: Medium resolution (720p)\n\n")
        results_file.write("Test set 3: High resolution (1080p)\n\n\n")

    def compute_average_runtime(self):
        avg_times = {}

        for algorithm in self.execution_times:
            avg_times[algorithm] = {}
            for test_set in self.execution_times[algorithm]:
                avg_times[algorithm][test_set] = mean(
                    self.execution_times[algorithm][test_set]
                )

        return avg_times

    def write_runtime(self, results_file, avg_times):
        results_file.write("### Average runtime (in seconds)\n")
        results_file.write("Algorithm \\ Test Set | Low Res | Med Res | High Res\n")
        results_file.write("---|---|---|---\n")
        for algorithm in avg_times:
            results_file.write(
                f"{algorithm}|\
                {avg_times[algorithm]['low_res']:7.3f}|\
                {avg_times[algorithm]['medium_res']:7.3f}|\
                {avg_times[algorithm]['high_res']:7.3f}\n"
            )
        results_file.write("\n")

    def write_sizes(self, results_file):
        results_file.write("### Average size (% of original image)\n")
        results_file.write("Algorithm \\ Test Set | Low Res | Med Res | High Res\n")
        results_file.write("---|---|---|---\n")
        for algorithm in self.image_sizes:
            results_file.write(
                f"{algorithm}|\
                {self.image_sizes[algorithm]['low_res']:7.3f}|\
                {self.image_sizes[algorithm]['medium_res']:7.3f}|\
                {self.image_sizes[algorithm]['high_res']:7.3f}\n"
            )

    def generate(self):
        file = self.open_results_file()
        self.write_header(file)
        self.write_runtime(file, self.compute_average_runtime())
        self.write_sizes(file)
