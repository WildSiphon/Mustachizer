import numpy as np
from scipy.ndimage import gaussian_filter
import cv2
import sys

class ColorConstancy:

    @classmethod
    def find_color(cls, image: np.array):
        """Compute lightning color using 2nd order grey-edge algorithm."""
        output = image.copy().astype(int)

        mask = cls.desaturize(output)

        cls.compute_norm_derivative(output, 2)

        white_light = cls.compute_minkowski_norm(output, 7)

        return (white_light*255).astype(np.int8)
    
    @classmethod
    def desaturize(cls, image: np.array):
        """Remove saturated points from the image."""
        mask = np.max(image, axis=2) >= 255
        image[mask] = 0
        return mask == False
    
    @classmethod
    def compute_norm_derivative(cls, image: np.array, sigma: float):
        """Compute the first order gaussian derivative."""
        for i in range(image.shape[2]):
            image[:, :, i] = np.abs(gaussian_filter(image[:, :, i], sigma=sigma, order=1))
    
    @classmethod
    def compute_minkowski_norm(cls, image: np.array, order):
        power = image ** order
        white = np.zeros((image.shape[2]), dtype=float)
        for i in range(image.shape[2]):
            white[i] = np.power(np.sum(power[:, :, i]), 1/order)
        norm = np.linalg.norm(white)
        if norm > 0:
            white /= norm
        return white

if __name__ == "__main__":
    im = cv2.imread(sys.argv[1])
    print(ColorConstancy.find_color(im))