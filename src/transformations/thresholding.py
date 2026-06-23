import cv2
import numpy as np

def apply_binarization(image, threshold=127, method='Binary', block_size=11, c=2):
    """
    Applies thresholding/binarization to the image with various methods.
    Methods:
    - 'Binary'
    - 'Binary Inverse'
    - 'Truncate'
    - 'To Zero'
    - 'To Zero Inverse'
    - 'Otsu'
    - 'Adaptive Mean'
    - 'Adaptive Gaussian'
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Ensure block_size is odd and >= 3 for adaptive thresholding
    if block_size < 3:
        block_size = 3
    elif block_size % 2 == 0:
        block_size += 1

    method_lower = method.lower()
    if method_lower == 'binary':
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    elif method_lower in ('binary inverse', 'binary_inv', 'binary inv'):
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
    elif method_lower in ('truncate', 'trunc'):
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_TRUNC)
    elif method_lower in ('to zero', 'tozero'):
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_TOZERO)
    elif method_lower in ('to zero inverse', 'tozero_inv', 'to zero inv'):
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_TOZERO_INV)
    elif method_lower == 'otsu':
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif method_lower in ('adaptive mean', 'adaptive_mean'):
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                       cv2.THRESH_BINARY, block_size, c)
    elif method_lower in ('adaptive gaussian', 'adaptive_gaussian'):
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, block_size, c)
    else:
        # Default fallback
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        
    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
