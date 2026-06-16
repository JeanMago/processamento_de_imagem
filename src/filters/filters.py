import cv2
import numpy as np

def apply_gaussian_blur(image, kernel_size=5, sigma=1.0):
    """
    Applies Gaussian Blur to the image.
    kernel_size: must be odd and positive.
    sigma: Gaussian kernel standard deviation.
    """
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigmaX=sigma)

def apply_median_blur(image, kernel_size=5):
    """
    Applies Median Blur to remove salt-and-pepper noise.
    kernel_size: must be odd and positive.
    """
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.medianBlur(image, kernel_size)

def apply_laplacian(image, ksize=3, scale=1, delta=0):
    """
    Applies Laplacian operator for edge detection.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize=ksize, scale=scale, delta=delta)
    abs_laplacian = cv2.convertScaleAbs(laplacian)
    return cv2.cvtColor(abs_laplacian, cv2.COLOR_GRAY2BGR)

def apply_sobel(image, direction='both', ksize=3):
    """
    Applies Sobel operator for edge detection.
    direction: 'horizontal', 'vertical', or 'both'.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    if direction == 'horizontal' or direction == 'both':
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
        abs_sobelx = cv2.convertScaleAbs(sobelx)
        
    if direction == 'vertical' or direction == 'both':
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)
        abs_sobely = cv2.convertScaleAbs(sobely)
        
    if direction == 'both':
        combined = cv2.addWeighted(abs_sobelx, 0.5, abs_sobely, 0.5, 0)
        return cv2.cvtColor(combined, cv2.COLOR_GRAY2BGR)
    elif direction == 'horizontal':
        return cv2.cvtColor(abs_sobelx, cv2.COLOR_GRAY2BGR)
    else:
        return cv2.cvtColor(abs_sobely, cv2.COLOR_GRAY2BGR)
