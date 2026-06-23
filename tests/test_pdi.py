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
    apply_grayscale, apply_isolate_color, apply_resize, apply_rotation,
    apply_scale
)
from utils.utils import cv2_to_pil, calculate_histogram

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

        # Test other binarization methods
        res_inv = apply_binarization(self.test_image, threshold=127, method='Binary Inverse')
        self.assertEqual(res_inv.shape, self.test_image.shape)
        
        res_otsu = apply_binarization(self.test_image, method='Otsu')
        self.assertEqual(res_otsu.shape, self.test_image.shape)
        
        res_mean = apply_binarization(self.test_image, method='Adaptive Mean', block_size=11, c=2)
        self.assertEqual(res_mean.shape, self.test_image.shape)

        res_gauss = apply_binarization(self.test_image, method='Adaptive Gaussian', block_size=11, c=2)
        self.assertEqual(res_gauss.shape, self.test_image.shape)

    def test_resize(self):
        res = apply_resize(self.test_image, 150, 80)
        self.assertEqual(res.shape, (80, 150, 3))

    def test_rotation(self):
        # Rotation by 90 degrees with bounds kept
        res_bounds = apply_rotation(self.test_image, 90, keep_bounds=True)
        # Standard rotation without keeping bounds
        res_no_bounds = apply_rotation(self.test_image, 45, keep_bounds=False)
        self.assertEqual(res_no_bounds.shape, self.test_image.shape)
        self.assertFalse(np.array_equal(res_no_bounds, self.test_image))

    def test_scale(self):
        res = apply_scale(self.test_image, 1.5, 2.0)
        self.assertEqual(res.shape, (200, 150, 3))

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

    def test_brightness_contrast_negative(self):
        img = np.ones((10, 10, 3), dtype=np.uint8) * 50
        res = apply_brightness_contrast(img, brightness=-60, contrast=0)
        self.assertTrue(np.all(res == 0))

    def test_grayscale_utils(self):
        gray_img = np.ones((10, 10), dtype=np.uint8) * 100
        pil_img = cv2_to_pil(gray_img)
        self.assertEqual(pil_img.size, (10, 10))
        hist = calculate_histogram(gray_img)
        self.assertEqual(len(hist), 1)
        self.assertEqual(hist[0][1], 'k')

if __name__ == '__main__':
    unittest.main()
