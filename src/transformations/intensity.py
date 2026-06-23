import cv2
import numpy as np

def apply_brightness_contrast(image, brightness=0, contrast=0):
    """
    Adjusts brightness and contrast.
    brightness: -100 to 100
    contrast: -100 to 100
    """
    # Correct contrast mapping: contrast = 0 maps to alpha = 1.0
    # Range [-100, 100] maps to [0.1, 3.0]
    if contrast >= 0:
        alpha = 1.0 + (contrast / 100.0) * 2.0  # [1.0, 3.0]
    else:
        alpha = 1.0 + (contrast / 100.0) * 0.9  # [0.1, 1.0)
        
    beta = brightness
    
    # Use float32 arithmetic and np.clip to avoid convertScaleAbs absolute-value behavior
    adjusted = np.clip(image.astype(np.float32) * alpha + beta, 0, 255).astype(np.uint8)
    return adjusted

def apply_invert_colors(image):
    """
    Inverts colors of the image.
    """
    return cv2.bitwise_not(image)

def apply_grayscale(image):
    """
    Converts image to grayscale.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

def apply_histogram_equalization(image):
    """
    Applies histogram equalization to the Y channel of YUV (to preserve color).
    """
    img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
    return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
