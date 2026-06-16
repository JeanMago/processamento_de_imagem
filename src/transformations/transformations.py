import cv2
import numpy as np

def apply_brightness_contrast(image, brightness=0, contrast=0):
    """
    Adjusts brightness and contrast.
    brightness: -100 to 100
    contrast: -100 to 100
    """
    # Contrast: mapping [-100, 100] to [0.1, 3.0]
    alpha = (contrast + 100) / 100.0 * 2.0 + 0.1
    # Brightness: mapping [-100, 100] to [-100, 100]
    beta = brightness
    
    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return adjusted

def apply_binarization(image, threshold=127):
    """
    Converts image to binary based on threshold.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

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

def apply_isolate_color(image, color_name='red'):
    """
    Isolates a specific color and converts the rest to grayscale.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Define color ranges in HSV
    ranges = {
        'red': ([0, 100, 100], [10, 255, 255], [160, 100, 100], [180, 255, 255]),
        'green': ([35, 100, 100], [85, 255, 255]),
        'blue': ([100, 100, 100], [140, 255, 255]),
        'yellow': ([20, 100, 100], [30, 255, 255]),
        'cyan': ([85, 100, 100], [100, 255, 255]),
        'magenta': ([140, 100, 100], [160, 255, 255])
    }
    
    if color_name not in ranges:
        return image
    
    target_range = ranges[color_name]
    
    if color_name == 'red':
        mask1 = cv2.inRange(hsv, np.array(target_range[0]), np.array(target_range[1]))
        mask2 = cv2.inRange(hsv, np.array(target_range[2]), np.array(target_range[3]))
        mask = cv2.bitwise_or(mask1, mask2)
    else:
        mask = cv2.inRange(hsv, np.array(target_range[0]), np.array(target_range[1]))
    
    # Create grayscale version
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    # Combine: isolated color where mask is 255, grayscale where mask is 0
    res = np.where(mask[:, :, None] == 255, image, gray_bgr)
    return res

def apply_histogram_equalization(image):
    """
    Applies histogram equalization to the Y channel of YUV (to preserve color).
    """
    img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
    return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
