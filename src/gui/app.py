import customtkinter as ctk
import cv2
import os
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageTk
import numpy as np

from ..services.image_service import ImageService
from ..utils.utils import cv2_to_pil, resize_to_fit, calculate_histogram
from ..filters.filters import apply_gaussian_blur, apply_median_blur, apply_laplacian, apply_sobel
from ..transformations.transformations import (
    apply_brightness_contrast, apply_binarization, apply_invert_colors, 
    apply_grayscale, apply_isolate_color, apply_histogram_equalization
)

class ImageApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDI PhotoPro - Advanced Image Editor")
        self.geometry("1600x1000")
        
        # Photoshop Dark Theme
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#1e1e1e")

        self.image_service = ImageService()
        self.current_file_path = None
        self.current_tool = "None"
        
        # Interaction State
        self.zoom_level = 1.0
        self.fg_color = "#ffffff"
        self.bg_color = "#000000"
        
        self.setup_ui_skeleton()
        self.setup_properties_panel()
        self.setup_canvas_area()
        self.load_predefined_images()
        self.bind_events()

    def setup_ui_skeleton(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        self.top_bar = ctk.CTkFrame(self, height=35, corner_radius=0, fg_color="#2b2b2b", border_width=1, border_color="#1a1a1a")
        self.top_bar.grid(row=0, column=0, columnspan=2, sticky="new")
        
        menus = [
            ("File", ["File", "Open...", "Save", "Exit"], self.handle_file_menu),
            ("Edit", ["Edit", "Undo", "Redo", "Reset Image"], self.handle_edit_menu),
            ("Image", ["Image", "Grayscale", "Invert", "Equalize"], self.handle_image_menu),
            ("Filter", ["Filter", "Gaussian Blur", "Median Filter", "Sobel Edges", "Laplacian"], self.handle_filter_menu),
            ("View", ["View", "Zoom In", "Zoom Out", "Fit Screen"], self.handle_view_menu),
            ("Window", ["Window", "Toggle Properties"], self.handle_window_menu)
        ]

        for label, vals, cmd in menus:
            m = ctk.CTkOptionMenu(self.top_bar, values=vals, command=cmd, width=80, height=25, fg_color="#2b2b2b", button_color="#2b2b2b", button_hover_color="#3d3d3d", dynamic_resizing=False)
            m.set(label); m.pack(side="left", padx=2)

        self.status_bar = ctk.CTkFrame(self, height=25, corner_radius=0, fg_color="#2b2b2b", border_width=1, border_color="#1a1a1a")
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="sew")
        self.status_label = ctk.CTkLabel(self.status_bar, text="Ready", font=ctk.CTkFont(size=11), text_color="#888")
        self.status_label.pack(side="left", padx=15)
        self.coords_label = ctk.CTkLabel(self.status_bar, text="X: 0, Y: 0", font=ctk.CTkFont(size=11), text_color="#888")
        self.coords_label.pack(side="right", padx=10)
        self.zoom_label = ctk.CTkLabel(self.status_bar, text="100% | RGB/8", font=ctk.CTkFont(size=11), text_color="#888")
        self.zoom_label.pack(side="right", padx=15)

    def bind_events(self):
        self.processed_canvas.bind("<Motion>", self.track_mouse)
        self.processed_canvas.bind("<MouseWheel>", self.handle_zoom)

    def track_mouse(self, event):
        self.coords_label.configure(text=f"X: {event.x}, Y: {event.y}")

    def handle_zoom(self, event):
        if event.delta > 0: self.handle_view_menu("Zoom In")
        else: self.handle_view_menu("Zoom Out")

    def handle_file_menu(self, choice):
        if choice == "Open...": self.open_image_dialog()
        elif choice == "Save": self.save_image_dialog()
        elif choice == "Exit": self.quit()

    def handle_edit_menu(self, choice):
        if choice == "Undo": self.undo_action()
        elif choice == "Redo": self.redo_action()
        elif choice == "Reset Image": self.reset_image()

    def handle_image_menu(self, choice):
        if choice == "Grayscale": self.apply_direct('grayscale')
        elif choice == "Invert": self.apply_direct('invert')
        elif choice == "Equalize": self.apply_direct('equalize')

    def handle_filter_menu(self, choice):
        if choice == "Gaussian Blur": self.apply_filter_permanent('gaussian')
        elif choice == "Median Filter": self.apply_filter_permanent('median')
        elif choice == "Sobel Edges": self.apply_filter_permanent('sobel')
        elif choice == "Laplacian": self.apply_filter_permanent('laplacian')

    def handle_view_menu(self, choice):
        if choice == "Zoom In": self.zoom_level *= 1.2
        elif choice == "Zoom Out": self.zoom_level /= 1.2
        elif choice == "Fit Screen": self.zoom_level = 1.0
        self.zoom_level = max(0.1, min(self.zoom_level, 5.0))
        self.zoom_label.configure(text=f"{int(self.zoom_level*100)}% | RGB/8")
        self.update_displays()

    def handle_window_menu(self, choice):
        if choice == "Toggle Properties":
            if self.prop_panel.winfo_ismapped(): self.prop_panel.grid_forget()
            else: self.prop_panel.grid(row=1, column=1, sticky="nse")

    def set_status(self, text): self.status_label.configure(text=text)

    def setup_properties_panel(self):
        self.prop_panel = ctk.CTkFrame(self, width=340, corner_radius=0, fg_color="#252525", border_width=1, border_color="#1a1a1a")
        self.prop_panel.grid(row=1, column=1, sticky="nse"); self.prop_panel.grid_propagate(False)
        self.prop_header = ctk.CTkFrame(self.prop_panel, height=40, fg_color="#333", corner_radius=0)
        self.prop_header.pack(fill="x")
        ctk.CTkLabel(self.prop_header, text="PROPERTIES & TOOLS", font=ctk.CTkFont(size=11, weight="bold"), text_color="#aaa").pack(pady=10)
        self.hud_panel = ctk.CTkTabview(self.prop_panel, fg_color="#2b2b2b", segmented_button_selected_color="#3d85c6")
        self.hud_panel.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tab_adjust = self.hud_panel.add("ADJUST"); self.tab_filters = self.hud_panel.add("FILTERS"); self.tab_color = self.hud_panel.add("COLOR"); self.tab_history = self.hud_panel.add("HISTORY")
        self.setup_adjust_tab(); self.setup_filters_tab_ps(); self.setup_color_tab_ps(); self.setup_history_tab_ps()

    def setup_adjust_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_adjust, fg_color="transparent"); scroll.pack(fill="both", expand=True)
        self.create_slider_group(scroll, "Brightness", -100, 100, 0, 'slider_bright', 'val_bright')
        self.create_slider_group(scroll, "Contrast", -100, 100, 0, 'slider_contrast', 'val_contrast')
        self.frame_bin_main = ctk.CTkFrame(scroll, fg_color="#333", corner_radius=8, border_width=1, border_color="#444"); self.frame_bin_main.pack(fill="x", pady=10, padx=5)
        self.bin_header = ctk.CTkFrame(self.frame_bin_main, fg_color="transparent"); self.bin_header.pack(fill="x", padx=10, pady=(10, 0))
        self.bin_enabled = ctk.BooleanVar(value=False)
        self.check_bin = ctk.CTkCheckBox(self.bin_header, text="THRESHOLDING", font=ctk.CTkFont(size=10, weight="bold"), variable=self.bin_enabled, command=self.apply_trans_live, checkbox_width=18, checkbox_height=18); self.check_bin.pack(side="left")
        self.val_bin = ctk.CTkLabel(self.bin_header, text="127", font=ctk.CTkFont(size=10), text_color="#3d85c6"); self.val_bin.pack(side="right")
        self.slider_bin = ctk.CTkSlider(self.frame_bin_main, from_=0, to=255, command=lambda v: [self.val_bin.configure(text=str(int(v))), self.apply_trans_live()]); self.slider_bin.set(127); self.slider_bin.pack(fill="x", padx=10, pady=(5, 15))
        ctk.CTkButton(self.tab_adjust, text="COMMIT ALL ADJUSTMENTS", command=self.commit_changes, fg_color="#3d85c6", hover_color="#2966a3", height=35, font=ctk.CTkFont(weight="bold")).pack(pady=15, padx=15, fill="x")

    def create_slider_group(self, parent, label, start, end, val, attr_name, val_attr):
        frame = ctk.CTkFrame(parent, fg_color="#333", corner_radius=8, border_width=1, border_color="#444"); frame.pack(fill="x", pady=5, padx=5)
        header = ctk.CTkFrame(frame, fg_color="transparent"); header.pack(fill="x", padx=10, pady=(8, 0))
        ctk.CTkLabel(header, text=label.upper(), font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(side="left")
        val_label = ctk.CTkLabel(header, text=str(val), font=ctk.CTkFont(size=10), text_color="#3d85c6"); val_label.pack(side="right"); setattr(self, val_attr, val_label)
        slider = ctk.CTkSlider(frame, from_=start, to=end, command=lambda v: [val_label.configure(text=f"{int(v):+}"), self.apply_trans_live()]); slider.set(val); slider.pack(fill="x", padx=10, pady=(5, 12)); setattr(self, attr_name, slider)

    def setup_filters_tab_ps(self):
        scroll = ctk.CTkScrollableFrame(self.tab_filters, fg_color="transparent"); scroll.pack(fill="both", expand=True)
        self.create_filter_widget(scroll, "Gaussian Blur", "slider_gauss", "val_gauss", 'gaussian')
        self.create_filter_widget(scroll, "Median Filter", "slider_median", "val_median", 'median')
        edge_frame = ctk.CTkFrame(scroll, fg_color="#333", corner_radius=8, border_width=1, border_color="#444"); edge_frame.pack(fill="x", pady=10, padx=5)
        ctk.CTkLabel(edge_frame, text="EDGE DETECTION MODES", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(pady=(10, 5))
        self.sobel_mode = ctk.CTkSegmentedButton(edge_frame, values=["Horizontal", "Vertical", "Combined"], height=30); self.sobel_mode.set("Combined"); self.sobel_mode.pack(fill="x", padx=10, pady=5)
        btn_row = ctk.CTkFrame(edge_frame, fg_color="transparent"); btn_row.pack(fill="x", padx=10, pady=(5, 15))
        ctk.CTkButton(btn_row, text="SOBEL", command=lambda: self.apply_filter_permanent('sobel'), height=28).pack(side="left", expand=True, padx=2)
        ctk.CTkButton(btn_row, text="LAPLACIAN", command=lambda: self.apply_filter_permanent('laplacian'), height=28, fg_color="transparent", border_width=1).pack(side="left", expand=True, padx=2)

    def create_filter_widget(self, parent, label, slider_attr, val_attr, filter_type):
        frame = ctk.CTkFrame(parent, fg_color="#333", corner_radius=8, border_width=1, border_color="#444"); frame.pack(fill="x", pady=5, padx=5)
        header = ctk.CTkFrame(frame, fg_color="transparent"); header.pack(fill="x", padx=10, pady=(8, 0))
        ctk.CTkLabel(header, text=label.upper(), font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(side="left")
        val_label = ctk.CTkLabel(header, text="1", font=ctk.CTkFont(size=10), text_color="#3d85c6"); val_label.pack(side="right")
        slider = ctk.CTkSlider(frame, from_=1, to=21, number_of_steps=10, command=lambda v: [val_label.configure(text=str(int(v))), self.apply_filters_live()]); slider.set(1); slider.pack(fill="x", padx=10, pady=(5, 5))
        setattr(self, val_attr, val_label); setattr(self, slider_attr, slider); ctk.CTkButton(frame, text=f"APPLY {filter_type.upper()}", command=lambda: self.apply_filter_permanent(filter_type), height=24, fg_color="#444", font=ctk.CTkFont(size=10)).pack(fill="x", padx=10, pady=(5, 10))

    def setup_color_tab_ps(self):
        scroll = ctk.CTkScrollableFrame(self.tab_color, fg_color="transparent"); scroll.pack(fill="both", expand=True)
        preset_frame = ctk.CTkFrame(scroll, fg_color="#333", corner_radius=8); preset_frame.pack(fill="x", pady=5, padx=5)
        ctk.CTkLabel(preset_frame, text="COLOR PRESETS", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(pady=8)
        for act in [('Grayscale', 'grayscale'), ('Invert Colors', 'invert'), ('Equalize Hist.', 'equalize')]:
            ctk.CTkButton(preset_frame, text=act[0], command=lambda a=act[1]: self.apply_direct(a), fg_color="#444", height=28).pack(pady=2, padx=10, fill="x")
        iso_frame = ctk.CTkFrame(scroll, fg_color="#333", corner_radius=8, border_width=1, border_color="#444"); iso_frame.pack(fill="x", pady=10, padx=5)
        ctk.CTkLabel(iso_frame, text="COLOR ISOLATION", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(pady=8)
        self.isolate_mode = ctk.CTkSegmentedButton(iso_frame, values=["None", "Red", "Green", "Blue", "Yellow", "Cyan", "Magenta"], command=lambda v: [self.isolate_var.set(v.lower()), self.apply_isolate_live()])
        self.isolate_mode.set("None"); self.isolate_mode.pack(fill="x", padx=10, pady=(0, 15))
        self.isolate_var = ctk.StringVar(value="None")

    def setup_history_tab_ps(self):
        self.hist_canvas = ctk.CTkCanvas(self.tab_history, bg="#1a1a1a", height=150, highlightthickness=0); self.hist_canvas.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(self.tab_history, text="STEP HISTORY", font=ctk.CTkFont(size=10, weight="bold")).pack(pady=5)
        self.btn_undo = ctk.CTkButton(self.tab_history, text="↩ Undo Step", command=self.undo_action, state="disabled", fg_color="#444"); self.btn_undo.pack(pady=5, padx=10, fill="x")
        self.btn_redo = ctk.CTkButton(self.tab_history, text="↪ Redo Step", command=self.redo_action, state="disabled", fg_color="#444"); self.btn_redo.pack(pady=5, padx=10, fill="x")
        self.btn_reset = ctk.CTkButton(self.tab_history, text="Reset to Original", command=self.reset_image, state="disabled", fg_color="#8c3d3d"); self.btn_reset.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(self.tab_history, text="ASSETS / LAYERS", font=ctk.CTkFont(size=10, weight="bold")).pack(pady=(20, 5))
        self.image_gallery = ctk.CTkScrollableFrame(self.tab_history, height=300, fg_color="#222"); self.image_gallery.pack(fill="both", expand=True, padx=5, pady=5)

    def setup_canvas_area(self):
        self.canvas_area = ctk.CTkFrame(self, fg_color="#121212", corner_radius=0); self.canvas_area.grid(row=1, column=0, sticky="nsew")
        self.quick_bar = ctk.CTkFrame(self.canvas_area, height=40, fg_color="#2b2b2b", corner_radius=0); self.quick_bar.pack(side="top", fill="x")
        ctk.CTkButton(self.quick_bar, text="↩", width=30, height=25, command=self.undo_action, fg_color="transparent").pack(side="left", padx=(10, 2), pady=5)
        ctk.CTkButton(self.quick_bar, text="↪", width=30, height=25, command=self.redo_action, fg_color="transparent").pack(side="left", padx=2, pady=5)
        ctk.CTkButton(self.quick_bar, text="RESET CANVAS", width=100, height=25, command=self.reset_image, fg_color="#8c3d3d", font=ctk.CTkFont(size=10, weight="bold")).pack(side="left", padx=10, pady=5)
        self.canvas_tabs = ctk.CTkFrame(self.canvas_area, height=30, fg_color="#333", corner_radius=0); self.canvas_tabs.pack(side="top", fill="x")
        self.tab_label = ctk.CTkLabel(self.canvas_tabs, text="  no_document.psd @ 100% (RGB/8) *  ", font=ctk.CTkFont(size=11), fg_color="#2b2b2b"); self.tab_label.pack(side="left", fill="y", padx=2)
        self.image_container = ctk.CTkFrame(self.canvas_area, fg_color="transparent"); self.image_container.pack(fill="both", expand=True, padx=20, pady=20)
        self.original_canvas = ctk.CTkLabel(self.image_container, text="", fg_color="#1a1a1a"); self.original_canvas.pack(side="left", fill="both", expand=True, padx=5)
        self.processed_canvas = ctk.CTkLabel(self.image_container, text="NO DOCUMENT OPEN", fg_color="#1a1a1a", font=ctk.CTkFont(size=14)); self.processed_canvas.pack(side="right", fill="both", expand=True, padx=5)

    def load_predefined_images(self):
        img_folder = "images"
        if not os.path.exists(img_folder): return
        files = [f for f in os.listdir(img_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        for file in files:
            path = os.path.join(img_folder, file)
            try:
                img = Image.open(path); img.thumbnail((80, 80))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
                btn = ctk.CTkButton(self.image_gallery, text=file, image=ctk_img, compound="top", command=lambda p=path: self.load_image(p), fg_color="#2b2b2b", font=ctk.CTkFont(size=10))
                btn._image = ctk_img; btn.pack(pady=5, padx=5, fill="x")
            except Exception as e: print(f"Thumbnail error: {e}")

    def load_image(self, path):
        try:
            self.image_service.load_image(path); self.current_file_path = path; self.update_displays(); self.enable_controls()
            self.set_status(f"Document Opened: {os.path.basename(path)}"); self.tab_label.configure(text=f"  {os.path.basename(path)} @ 100% (RGB/8) *  "); self.reset_ui_params()
        except Exception as e: messagebox.showerror("Erro", f"Failed: {e}")

    def reset_ui_params(self):
        self.slider_gauss.set(1); self.val_gauss.configure(text="1")
        self.slider_median.set(1); self.val_median.configure(text="1")
        self.slider_bright.set(0); self.val_bright.configure(text="0")
        self.slider_contrast.set(0); self.val_contrast.configure(text="0")
        self.slider_bin.set(127); self.val_bin.configure(text="127"); self.bin_enabled.set(False)
        self.isolate_mode.set("None"); self.isolate_var.set("None")

    def reset_image(self):
        if self.image_service.reset() is not None: self.update_displays(); self.reset_ui_params(); self.set_status("Document Reset")

    def open_image_dialog(self):
        path = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.tiff")])
        if path: self.load_image(path)

    def save_image_dialog(self):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPG", "*.jpg")])
        if path and self.image_service.save_image(path): messagebox.showinfo("Success", "File Exported"); self.set_status(f"Exported: {os.path.basename(path)}")

    def enable_controls(self):
        for btn in [self.btn_undo, self.btn_redo, self.btn_reset]: btn.configure(state="normal")

    def update_displays(self, processed=None):
        if self.image_service.original_image is None: return
        w_scaled = int(600 * self.zoom_level); h_scaled = int(500 * self.zoom_level)
        orig_resized = resize_to_fit(self.image_service.original_image, w_scaled, h_scaled)
        pil_orig = cv2_to_pil(orig_resized)
        ctk_orig = ctk.CTkImage(light_image=pil_orig, dark_image=pil_orig, size=(pil_orig.width, pil_orig.height))
        self.original_canvas.configure(image=ctk_orig, text=""); self.original_canvas._image = ctk_orig
        display_img = processed if processed is not None else self.image_service.current_image
        proc_resized = resize_to_fit(display_img, w_scaled, h_scaled)
        pil_proc = cv2_to_pil(proc_resized)
        ctk_proc = ctk.CTkImage(light_image=pil_proc, dark_image=pil_proc, size=(pil_proc.width, pil_proc.height))
        self.processed_canvas.configure(image=ctk_proc, text=""); self.processed_canvas._image = ctk_proc; self.update_histogram(display_img)

    def update_histogram(self, image):
        self.hist_canvas.delete("all")
        hists = calculate_histogram(image); w, h = 300, 150; max_val = max([h[0].max() for h in hists]) if hists else 1
        colors_map = {'b': '#0000ff', 'g': '#00ff00', 'r': '#ff0000'}
        for hist_counts, col in hists:
            points = []
            for i, count in enumerate(hist_counts): points.append(((i / 255) * w, h - (count / max_val) * h))
            self.hist_canvas.create_line(points, fill=colors_map[col], width=1)

    def apply_filters_live(self, _=None):
        if self.image_service.current_image is None: return
        img = self.image_service.current_image.copy()
        if self.slider_gauss.get() > 1: img = apply_gaussian_blur(img, kernel_size=int(self.slider_gauss.get()))
        if self.slider_median.get() > 1: img = apply_median_blur(img, kernel_size=int(self.slider_median.get()))
        self.update_displays(img)

    def apply_filter_permanent(self, filter_type):
        if self.image_service.current_image is None: return
        img = self.image_service.current_image.copy()
        if filter_type == 'gaussian': img = apply_gaussian_blur(img, kernel_size=int(self.slider_gauss.get()))
        elif filter_type == 'median': img = apply_median_blur(img, kernel_size=int(self.slider_median.get()))
        elif filter_type == 'laplacian': img = apply_laplacian(img)
        elif filter_type == 'sobel':
            mode_map = {"Horizontal": "horizontal", "Vertical": "vertical", "Combined": "both"}
            img = apply_sobel(img, direction=mode_map.get(self.sobel_mode.get(), "both"))
        self.image_service.update_current_image(img); self.update_displays(); self.set_status(f"Filter Applied: {filter_type}")

    def apply_trans_live(self, _=None):
        if self.image_service.current_image is None: return
        img = self.image_service.current_image.copy()
        img = apply_brightness_contrast(img, brightness=self.slider_bright.get(), contrast=self.slider_contrast.get())
        if self.bin_enabled.get(): img = apply_binarization(img, threshold=int(self.slider_bin.get()))
        self.update_displays(img)

    def apply_isolate_live(self):
        if self.image_service.current_image is None: return
        if self.isolate_var.get() == "None": self.update_displays(); return
        img = apply_isolate_color(self.image_service.current_image, self.isolate_var.get()); self.update_displays(img)

    def apply_direct(self, action):
        if self.image_service.current_image is None: return
        if action == 'invert': img = apply_invert_colors(self.image_service.current_image)
        elif action == 'grayscale': img = apply_grayscale(self.image_service.current_image)
        elif action == 'equalize': img = apply_histogram_equalization(self.image_service.current_image)
        self.image_service.update_current_image(img); self.update_displays(); self.set_status(f"Action: {action}")

    def commit_changes(self):
        if self.image_service.current_image is None: return
        img = self.image_service.current_image.copy()
        img = apply_brightness_contrast(img, brightness=self.slider_bright.get(), contrast=self.slider_contrast.get())
        if self.bin_enabled.get(): img = apply_binarization(img, threshold=int(self.slider_bin.get()))
        self.image_service.update_current_image(img); self.update_displays(); self.reset_ui_params(); self.set_status("Adjustments Committed")

    def undo_action(self):
        if self.image_service.undo() is not None: self.update_displays(); self.set_status("Step Reverted")

    def redo_action(self):
        if self.image_service.redo() is not None: self.update_displays(); self.set_status("Step Redone")

if __name__ == "__main__":
    app = ImageApp(); app.mainloop()
