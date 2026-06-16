import unittest
import numpy as np
import cv2
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from filters.filters import apply_gaussian_blur, apply_median_blur, apply_laplacian, apply_sobel
from transformations.transformations import (
    apply_brightness_contrast, apply_binarization, apply_invert_colors, 
    apply_grayscale, apply_isolate_color
)

class TestPDI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a dummy image for testing
        cls.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.rectangle(cls.test_image, (25, 25), (75, 75), (255, 255, 255), -1)

    def test_gaussian_blur(self):
        res = apply_gaussian_blur(self.test_image, kernel_size=5)
        self.assertEqual(res.shape, self.test_image.shape)
        self.assertFalse(np.array_equal(res, self.test_image))

    def test_median_blur(self):
        res = apply_median_blur(self.test_image, kernel_size=5)
        self.assertEqual(res.shape, self.test_image.shape)

    def test_laplacian(self):
        res = apply_laplacian(self.test_image)
        self.assertEqual(res.shape, self.test_image.shape)

    def test_sobel(self):
        res = apply_sobel(self.test_image, direction='both')
        self.assertEqual(res.shape, self.test_image.shape)

    def test_brightness_contrast(self):
        res = apply_brightness_contrast(self.test_image, brightness=50, contrast=50)
        self.assertEqual(res.shape, self.test_image.shape)

    def test_binarization(self):
        res = apply_binarization(self.test_image, threshold=127)
        self.assertEqual(res.shape, self.test_image.shape)
        # Check if output is binary (0 or 255)
        unique_values = np.unique(res)
        for val in unique_values:
            self.assertIn(val, [0, 255])

    def test_invert_colors(self):
        res = apply_invert_colors(self.test_image)
        self.assertEqual(res.shape, self.test_image.shape)
        self.assertTrue(np.array_equal(res, cv2.bitwise_not(self.test_image)))

    def test_grayscale(self):
        res = apply_grayscale(self.test_image)
        self.assertEqual(res.shape, self.test_image.shape)
        # Check if R=G=B
        self.assertTrue(np.all(res[:,:,0] == res[:,:,1]))
        self.assertTrue(np.all(res[:,:,1] == res[:,:,2]))

    def test_isolate_color(self):
        res = apply_isolate_color(self.test_image, 'red')
        self.assertEqual(res.shape, self.test_image.shape)

if __name__ == '__main__':
    unittest.main()
