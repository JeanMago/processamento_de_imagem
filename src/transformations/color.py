import cv2
import numpy as np

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
