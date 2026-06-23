import cv2
import numpy as np

def apply_resize(image, width, height, interpolation=cv2.INTER_LINEAR):
    """
    Resizes the image to specified width and height.
    """
    if width <= 0 or height <= 0:
        return image
    return cv2.resize(image, (width, height), interpolation=interpolation)

def apply_rotation(image, angle, keep_bounds=True):
    """
    Rotates the image by a given angle (in degrees).
    If keep_bounds is True, the output image dimensions are adjusted to fit the rotated image.
    If keep_bounds is False, the output image dimensions are same as input (cropped).
    """
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    
    # Calculate rotation matrix
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    if keep_bounds:
        # Calculate new bounds
        cos_val = np.abs(M[0, 0])
        sin_val = np.abs(M[0, 1])
        
        new_w = int((h * sin_val) + (w * cos_val))
        new_h = int((h * cos_val) + (w * sin_val))
        
        # Adjust translation in matrix to ensure center alignment and no cutoff
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]
        
        rotated = cv2.warpAffine(image, M, (new_w, new_h))
    else:
        rotated = cv2.warpAffine(image, M, (w, h))
        
    return rotated

def apply_scale(image, scale_x, scale_y=None, interpolation=cv2.INTER_LINEAR):
    """
    Scales the image by scale_x and scale_y factors.
    """
    if scale_y is None:
        scale_y = scale_x
    if scale_x <= 0 or scale_y <= 0:
        return image
    h, w = image.shape[:2]
    new_w = int(w * scale_x)
    new_h = int(h * scale_y)
    if new_w <= 0 or new_h <= 0:
        return image
    return cv2.resize(image, (new_w, new_h), interpolation=interpolation)
