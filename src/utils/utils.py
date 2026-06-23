import cv2
import numpy as np
from PIL import Image, ImageTk

def cv2_to_pil(image):
    """Converts an OpenCV image (BGR or Grayscale) to a PIL Image (RGB)."""
    if len(image.shape) == 2 or image.shape[2] == 1:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    else:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(image_rgb)

def pil_to_tk(pil_image):
    """Converts a PIL Image to a Tkinter-compatible PhotoImage."""
    return ImageTk.PhotoImage(pil_image)

def calculate_histogram(image):
    """
    Calculates the histogram for each channel.
    Returns a list of (counts, color) for R, G, B or Grayscale.
    """
    if len(image.shape) == 2 or image.shape[2] == 1:
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        return [(hist.flatten(), 'k')]
        
    hist_data = []
    colors = ('b', 'g', 'r')
    for i, col in enumerate(colors):
        hist = cv2.calcHist([image], [i], None, [256], [0, 256])
        hist_data.append((hist.flatten(), col))
    return hist_data

def resize_to_fit(image, max_width, max_height):
    """Resizes an OpenCV image to fit within max dimensions while preserving aspect ratio."""
    h, w = image.shape[:2]
    aspect = w / h if h != 0 else 1
    
    if w > max_width:
        w = max_width
        h = int(w / aspect) if aspect != 0 else 1
    
    if h > max_height:
        h = max_height
        w = int(h * aspect)
        
    w = max(1, w)
    h = max(1, h)
    return cv2.resize(image, (w, h), interpolation=cv2.INTER_AREA)
