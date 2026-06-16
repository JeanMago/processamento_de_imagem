import cv2
import os

class ImageService:
    def __init__(self):
        self.original_image = None
        self.current_image = None
        self.history = []
        self.history_index = -1

    def load_image(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        image = cv2.imread(file_path)
        if image is None:
            raise ValueError("Failed to load image.")
        
        self.original_image = image.copy()
        self.current_image = image.copy()
        self.history = [self.current_image.copy()]
        self.history_index = 0
        return self.current_image

    def save_image(self, file_path):
        if self.current_image is None:
            raise ValueError("No image to save.")
        
        success = cv2.imwrite(file_path, self.current_image)
        return success

    def update_current_image(self, new_image, add_to_history=True):
        self.current_image = new_image.copy()
        if add_to_history:
            # Remove any forward history if we are in the middle
            self.history = self.history[:self.history_index + 1]
            self.history.append(self.current_image.copy())
            self.history_index += 1
            
            # Limit history size to 20 steps
            if len(self.history) > 20:
                self.history.pop(0)
                self.history_index -= 1

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.history[self.history_index].copy()
            return self.current_image
        return None

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_image = self.history[self.history_index].copy()
            return self.current_image
        return None

    def reset(self):
        if self.original_image is not None:
            self.update_current_image(self.original_image)
            return self.current_image
        return None
