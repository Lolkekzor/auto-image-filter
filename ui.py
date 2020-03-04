import subprocess
from PIL import Image
import os
import time

from threading import Thread, Lock
from PyQt5.QtWidgets import (
    QPushButton,
    QWidget,
    QVBoxLayout,
    QLabel,
    QFileDialog,
    QApplication,
)
from PyQt5.QtGui import QPixmap
from filters import (
    apply_gamma_enhance,
    apply_hdr_wls_enhance,
    apply_hdr_anisotropic_enhance,
    apply_hdr_bilateral_enhance,
)


class UI:

    # FILTERS[0] - name of the filter
    # FILTERS[1] - path of the filtered image
    # FILTERS[2] - function that filters the image(src_path, dst_path)
    FILTERS = [
        ("Gamma correction", "gamma.jpg", apply_gamma_enhance),
        ("HDR with WLS", "wls.jpg", apply_hdr_wls_enhance),
        ("HDR with anisotropic", "anisotropic.jpg", apply_hdr_anisotropic_enhance),
        ("HDR with bilateral", "bilateral.jpg", apply_hdr_bilateral_enhance),
    ]
    # CACHE_PATH - where to save the processed images
    CACHE_PATH = "ui/"

    def __init__(self):
        self.app = QApplication([])
        self.window = QWidget()
        self.layout = QVBoxLayout()

        self.init_buttons()
        self.init_labels()

        # Marks the number of loading filters, can only open image if 0
        self.loading = 0
        self.loading_lock = Lock()

        self.window.setLayout(self.layout)
        self.window.show()
        self.app.exec_()

    def init_labels(self):
        self.image_label = QLabel()
        self.layout.addWidget(self.image_label)

    def init_buttons(self):
        self.open_image_button = QPushButton("Open Image")
        self.open_image_button.clicked.connect(lambda: self.open_image())
        self.open_image_button.show()
        self.layout.addWidget(self.open_image_button)

        self.buttons = []
        for filter in self.FILTERS:
            button = QPushButton(filter[0])
            # connect adds some parameters by default, so adding *click_args gets rid of them
            # and f=filter keeps the right scope for the filter variable sent as parameter
            button.clicked.connect(
                lambda *click_args, f=filter: Thread(
                    target=self.apply_filter, args=(f)
                ).start()
            )
            button.setEnabled(False)
            button.show()
            self.buttons.append(button)
            self.layout.addWidget(button)

    def open_image(self):
        self.file_name = QFileDialog.getOpenFileName()[0]
        if self.file_name == '':
            return
        # check if the selected file is an image
        try:
            Image.open(self.file_name)
        except IOError:
            self.open_image_button.setText("Open Image - file is not an image")
            for button in self.buttons:
                button.setEnabled(False)
            return

        # display the image in the ui
        self.open_image_button.setText("Open Image")
        image = QPixmap(self.file_name)
        self.image_label.setPixmap(image)
        # after opening a new image we delete the old processed images and enable the filter buttons
        self.delete_cached_images()
        for button in self.buttons:
            button.setEnabled(True)

    def delete_cached_images(self):
        for filter in self.FILTERS:
            try:
                os.unlink(self.CACHE_PATH + filter[1])
            except OSError:
                pass

    def apply_filter(self, filter_name, filter_path, filter_function):
        """
        Applies the selected filter on the opened image
        If the image does not already exist, then it is processed and the does not allow to open a new
        image until it is finished
        """
        filter = (filter_name, filter_path, filter_function)
        if not os.path.exists(self.CACHE_PATH + filter[1]):
            self.loading_lock.acquire()
            self.loading = self.loading + 1
            self.open_image_button.setEnabled(False)
            self.loading_lock.release()

            Thread(target=self.mark_loading_process, args=(filter)).start()
            # filter[2] is the filter function
            filter[2](self.file_name, self.CACHE_PATH + filter[1])

            self.loading_lock.acquire()
            self.loading = self.loading - 1
            if self.loading == 0:
                self.open_image_button.setEnabled(True)
            self.loading_lock.release()

        return_status = subprocess.call(["open", self.CACHE_PATH + filter[1]])
        if return_status != 0:
            filter_index = self.FILTERS.index(filter)
            self.mark_error_on_button(self.buttons[filter_index])

    def mark_error_on_button(self, button):
        button.setText("Error")
        button.setEnabled(False)

    def mark_loading_process(self, filter_name, filter_path, filter_function):
        filter = (filter_name, filter_path, filter_function)
        filter_index = self.FILTERS.index(filter)
        # waiting at most waiting_time*1.5 seconds for the filter to finish, otherwise force finish
        waiting_time = 40
        for time_index in range(waiting_time):
            self.buttons[filter_index].setText(filter[0] + " Loading .")
            time.sleep(0.5)
            self.buttons[filter_index].setText(filter[0] + " Loading ..")
            time.sleep(0.5)
            self.buttons[filter_index].setText(filter[0] + " Loading ...")
            time.sleep(0.5)
            # if the file exists means that the filtering process is done and we can exit
            if os.path.exists(self.CACHE_PATH + filter[1]):
                break
        if time_index == waiting_time - 1:
            self.mark_error_on_button(self.buttons[filter_index])
        else:
            self.buttons[filter_index].setText(filter[0])


if __name__ == "__main__":
    UI()
