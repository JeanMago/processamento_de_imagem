# PDI PhotoPro - Advanced Image Editor

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet.svg)
![License](https://img.shields.io/badge/license-MIT-important.svg)

**PDI PhotoPro** is a professional-grade desktop application for Digital Image Processing (PDI) inspired by the Adobe Photoshop workflow. Developed with Python, OpenCV, and CustomTkinter, it offers a robust environment for applying spatial filters, point-to-point transformations, and color analysis through a modern and intuitive "Studio" interface.

---

## 🎨 Professional Interface (Photoshop Style)

- **Intuitive Properties Panel:** All adjustments (Brightness, Contrast, Threshold) and Filters are grouped in high-fidelity cards with real-time numeric feedback.
- **Modern UI Components:** Uses Segmented Buttons for mode selection and dynamic sliders.
- **HighDPI Support:** Native rendering using `ctk.CTkImage` ensures crystal clear visuals on 4K and scaled displays.
- **Interactive Workspace:** Real-time Zoom (Mouse Wheel), coordinate tracking, and a Quick Actions bar for Undo/Redo/Reset operations.

---

## 🚀 Key Features

### 1. Spatial Filtering (FILTERS)
- **Gaussian Blur:** High-quality smoothing with adjustable kernel intensity.
- **Median Filter:** Effective salt-and-pepper noise removal.
- **Edge Detection:**
    - **Sobel:** Horizontal, Vertical, and Combined modes via modern segmented controls.
    - **Laplacian:** Fine edge enhancement.

### 2. Point Transformations (ADJUST)
- **Brightness & Contrast:** Continuous linear adjustment with live preview.
- **Binarization (Thresholding):** Segmentation tool with an independent toggle and precise threshold control (0-255).
- **Color Presets:** One-click Grayscale conversion, Color Inversion (Negative), and Global Histogram Equalization.

### 3. Color Isolation (COLOR)
- **Targeted Selection:** Isolate specific hues (**Red, Green, Blue, Yellow, Cyan, Magenta**) while converting the rest of the image to grayscale. Ideal for technical analysis and artistic effects.

### 4. Advanced Workflow (HISTORY)
- **Undo/Redo System:** Navigate back and forth through your editing history (up to 20 steps).
- **RGB Histogram:** Real-time synchronization of color frequency data.
- **Assets/Layers Gallery:** Quick access to predefined sample images for testing.

---

## 💻 Installation

### Prerequisites
- Python 3.8 or higher.
- `pip` (Python package manager).

### Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/pdi-photopro.git
   cd pdi-photopro
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Or install manually: `pip install opencv-python numpy customtkinter pillow`)*

3. **Run the application:**
   ```bash
   python main.py
   ```

---

## 📂 Project Structure

```text
project/
├── images/             # Sample image bank
├── src/
│   ├── filters/        # PDI Algorithms: Smoothing and Edges
│   ├── transformations/# PDI Algorithms: Point-to-point and Colors
│   ├── gui/            # Modern View: CustomTkinter App Logic
│   ├── services/       # Controller: State management and I/O
│   └── utils/          # Helpers: Conversions and Resizing
├── tests/              # Unit tests for algorithm validation
├── main.py             # Entry point
└── requirements.txt    # Project dependencies
```

---

## 🛠️ Built With

- **[OpenCV](https://opencv.org/):** The core engine for high-performance image processing.
- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter):** A modern wrapped for Tkinter with dark mode and professional widgets.
- **[NumPy](https://numpy.org/):** Efficient matrix manipulation for image data.
- **[Pillow (PIL)](https://python-pillow.org/):** Image loading and GUI integration.

---

