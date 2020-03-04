import cv2
import numpy as np

from hdr_enhance.wls_filter import wlsFilter
from hdr_enhance.srs import SRS
from hdr_enhance.virtual_ev import VIG
from hdr_enhance.tonemap import tonemap
from hdr_enhance.anisotropic import anisodiff


class FakeHDR:
    def __init__(self, flag):
        self.weighted_fusion = flag
        self.wls = wlsFilter
        self.srs = SRS
        self.vig = VIG
        self.tonemap = tonemap
        self.anisodiff = anisodiff

    def process(self, image, use_anisotropic=False, use_bilateral_filtering=False):
        """
        image - open cv image to be enhanced
        HDR enhancement requires a edge-preserving smoothing filter
            if use_anisotropic is True anisotropic diffusion algorithm will be used - Good results, good time
            if use_bilateral_filtering is True a bilateral filter will be used - Good results, best time
            if both above are False WLS ( Weighted least-squares ) algorithm will be used - Best results, worst time
        """
        # The following lines normalize the image format to grayscale
        if len(image.shape) < 3:
            print("Cannot process grayscale images")
            exit(1)
        elif image.shape[2] == 4:
            image = image[:, :, 0:3]
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) / 255.0

        # This brings the intensity of pixels from the range [0, 255] to [0, 1]
        image = 1.0 * image / 255
        L = 1.0 * grayscale

        # The following filters bring out the details in an image
        # Anisotropic diffusion is much faster in runtime (10x), but has worse results visually (halo artifacts)
        # Bilateral filter is the fastest and has close visual results to WLS
        if use_anisotropic:
            Ig = self.anisodiff(grayscale, 100, 12, 0.2, (1.0, 1.0), 1)
        elif use_bilateral_filtering:
            Ig = cv2.bilateralFilter((grayscale * 255.0).astype("float32"), 25, 30, 100)
            Ig = Ig / 255.0
        else:
            Ig = self.wls(grayscale)

        # Mathematical wizardry
        R = np.log(L + 1e-22) - np.log(Ig + 1e-22)
        R = self.srs(R, L)
        I_K = self.vig(L, 1.0 - L)

        # Tadaa, processed image
        # This line performs a HDR tonemap using weighted_fusion
        return self.tonemap(image, L, R, I_K, self.weighted_fusion)
