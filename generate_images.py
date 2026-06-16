import numpy as np
import cv2
import os

def generate_sample_images():
    if not os.path.exists('images'):
        os.makedirs('images')
    
    # 1. Paisagem (Synthetic)
    img1 = np.zeros((400, 600, 3), dtype=np.uint8)
    img1[:200, :] = [255, 200, 150] # Sky
    img1[200:, :] = [100, 200, 100] # Grass
    cv2.circle(img1, (100, 100), 50, (0, 255, 255), -1) # Sun
    cv2.imwrite('images/paisagem.jpg', img1)
    
    # 2. Retrato (Synthetic)
    img2 = np.full((400, 400, 3), 200, dtype=np.uint8)
    cv2.circle(img2, (200, 200), 100, (150, 150, 255), -1) # Face-ish
    cv2.imwrite('images/retrato.jpg', img2)
    
    # 3. Textura
    img3 = np.random.randint(0, 255, (400, 400, 3), dtype=np.uint8)
    cv2.imwrite('images/textura.png', img3)
    
    # 4. Formas Geométricas
    img4 = np.zeros((400, 400, 3), dtype=np.uint8)
    cv2.rectangle(img4, (50, 50), (150, 150), (255, 0, 0), -1)
    cv2.circle(img4, (300, 100), 60, (0, 255, 0), -1)
    cv2.line(img4, (50, 300), (350, 350), (0, 0, 255), 10)
    cv2.imwrite('images/formas.png', img4)
    
    print("Sample images generated in 'images/' folder.")

if __name__ == "__main__":
    generate_sample_images()
