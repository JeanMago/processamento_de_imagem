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
    apply_grayscale, apply_isolate_color, apply_histogram_equalization,
    apply_resize, apply_rotation, apply_scale
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
        self.setup_canvas_area()
        self.setup_properties_panel()
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

        # Create resizable pane layout for main interface
        import tkinter as tk
        self.main_pane = tk.PanedWindow(self, orient="horizontal", bd=0, sashwidth=4, bg="#1a1a1a", opaqueresize=True)
        self.main_pane.grid(row=1, column=0, columnspan=2, sticky="nsew")

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
            if self.prop_panel.winfo_ismapped():
                self.main_pane.forget(self.prop_panel)
            else:
                self.main_pane.add(self.prop_panel, minsize=240)
                self.main_pane.paneconfig(self.prop_panel, stretch="never")

    def set_status(self, text): self.status_label.configure(text=text)

    def setup_properties_panel(self):
        self.prop_panel = ctk.CTkFrame(self.main_pane, width=280, corner_radius=0, fg_color="#252525", border_width=1, border_color="#1a1a1a")
        self.prop_panel.pack_propagate(False)
        self.main_pane.add(self.prop_panel, minsize=240)
        self.main_pane.paneconfig(self.prop_panel, stretch="never")
        self.prop_header = ctk.CTkFrame(self.prop_panel, height=40, fg_color="#333", corner_radius=0)
        self.prop_header.pack(fill="x")
        ctk.CTkLabel(self.prop_header, text="PROPERTIES & TOOLS", font=ctk.CTkFont(size=11, weight="bold"), text_color="#aaa").pack(pady=10)
        self.hud_panel = ctk.CTkTabview(self.prop_panel, fg_color="#2b2b2b", segmented_button_selected_color="#3d85c6")
        self.hud_panel._segmented_button.configure(font=ctk.CTkFont(size=9, weight="bold"))
        self.hud_panel.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tab_adjust = self.hud_panel.add("☀️ ADJUST")
        self.tab_filters = self.hud_panel.add("✨ FILTERS")
        self.tab_color = self.hud_panel.add("🎨 COLOR")
        self.tab_transforms = self.hud_panel.add("📐 TRANSFORMS")
        self.tab_history = self.hud_panel.add("📜 HISTORY")
        self.setup_adjust_tab()
        self.setup_filters_tab_ps()
        self.setup_color_tab_ps()
        self.setup_transforms_tab_ps()
        self.setup_history_tab_ps()

    def setup_adjust_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_adjust, fg_color="transparent"); scroll.pack(fill="both", expand=True)
        self.create_slider_group(scroll, "Brightness", -100, 100, 0, 'slider_bright', 'val_bright')
        self.create_slider_group(scroll, "Contrast", -100, 100, 0, 'slider_contrast', 'val_contrast')
        self.frame_bin_main = ctk.CTkFrame(scroll, fg_color="#333", corner_radius=8, border_width=1, border_color="#444"); self.frame_bin_main.pack(fill="x", pady=10, padx=5)
        self.bin_header = ctk.CTkFrame(self.frame_bin_main, fg_color="transparent"); self.bin_header.pack(fill="x", padx=10, pady=(10, 0))
        self.bin_enabled = ctk.BooleanVar(value=False)
        self.check_bin = ctk.CTkCheckBox(self.bin_header, text="THRESHOLDING", font=ctk.CTkFont(size=10, weight="bold"), variable=self.bin_enabled, command=self.apply_trans_live, checkbox_width=18, checkbox_height=18); self.check_bin.pack(side="left")
        self.val_bin = ctk.CTkLabel(self.bin_header, text="127", font=ctk.CTkFont(size=10), text_color="#3d85c6"); self.val_bin.pack(side="right")
        
        self.bin_method = ctk.StringVar(value="Binary")
        self.opt_bin_method = ctk.CTkOptionMenu(
            self.frame_bin_main,
            variable=self.bin_method,
            values=["Binary", "Binary Inverse", "Truncate", "To Zero", "To Zero Inverse", "Otsu", "Adaptive Mean", "Adaptive Gaussian"],
            command=self.on_bin_method_change,
            height=25,
            fg_color="#444",
            button_color="#555",
            button_hover_color="#666"
        )
        self.opt_bin_method.pack(fill="x", padx=10, pady=(5, 5))

        self.slider_bin = ctk.CTkSlider(self.frame_bin_main, from_=0, to=255, command=lambda v: [self.val_bin.configure(text=str(int(v))), self.apply_trans_live()]); self.slider_bin.set(127); self.slider_bin.pack(fill="x", padx=10, pady=(5, 10))
        
        self.frame_adaptive = ctk.CTkFrame(self.frame_bin_main, fg_color="transparent")
        
        fs_block = ctk.CTkFrame(self.frame_adaptive, fg_color="transparent")
        fs_block.pack(fill="x", pady=2)
        ctk.CTkLabel(fs_block, text="Block Size (Odd):", font=ctk.CTkFont(size=9), text_color="#aaa").pack(side="left")
        self.val_bin_block_size = ctk.CTkLabel(fs_block, text="11", font=ctk.CTkFont(size=9), text_color="#3d85c6")
        self.val_bin_block_size.pack(side="right")
        
        self.slider_bin_block_size = ctk.CTkSlider(self.frame_adaptive, from_=3, to=99, number_of_steps=48, command=self.on_adaptive_param_change)
        self.slider_bin_block_size.set(11)
        self.slider_bin_block_size.pack(fill="x", padx=5, pady=(0, 5))
        
        fs_c = ctk.CTkFrame(self.frame_adaptive, fg_color="transparent")
        fs_c.pack(fill="x", pady=2)
        ctk.CTkLabel(fs_c, text="Constant C:", font=ctk.CTkFont(size=9), text_color="#aaa").pack(side="left")
        self.val_bin_c = ctk.CTkLabel(fs_c, text="2", font=ctk.CTkFont(size=9), text_color="#3d85c6")
        self.val_bin_c.pack(side="right")
        
        self.slider_bin_c = ctk.CTkSlider(self.frame_adaptive, from_=-20, to=20, command=self.on_adaptive_param_change)
        self.slider_bin_c.set(2)
        self.slider_bin_c.pack(fill="x", padx=5, pady=(0, 5))

        ctk.CTkButton(self.tab_adjust, text="COMMIT ALL ADJUSTMENTS", command=self.commit_changes, fg_color="#3d85c6", hover_color="#2966a3", height=35, font=ctk.CTkFont(weight="bold")).pack(pady=15, padx=15, fill="x")

    def create_slider_group(self, parent, label, start, end, val, attr_name, val_attr):
        frame = ctk.CTkFrame(parent, fg_color="#333", corner_radius=8, border_width=1, border_color="#444"); frame.pack(fill="x", pady=5, padx=5)
        header = ctk.CTkFrame(frame, fg_color="transparent"); header.pack(fill="x", padx=10, pady=(8, 0))
        ctk.CTkLabel(header, text=label.upper(), font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(side="left")
        val_label = ctk.CTkLabel(header, text=str(val), font=ctk.CTkFont(size=10), text_color="#3d85c6"); val_label.pack(side="right"); setattr(self, val_attr, val_label)
        slider = ctk.CTkSlider(frame, from_=start, to=end, command=lambda v: [val_label.configure(text=f"{int(v):+}"), self.apply_trans_live()]); slider.set(val); slider.pack(fill="x", padx=10, pady=(5, 12)); setattr(self, attr_name, slider)

    def setup_filters_tab_ps(self):
        scroll = ctk.CTkScrollableFrame(self.tab_filters, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        choice_frame = ctk.CTkFrame(scroll, fg_color="#242424", corner_radius=8, border_width=1, border_color="#3a3a3a")
        choice_frame.pack(fill="x", pady=5, padx=5)
        ctk.CTkLabel(choice_frame, text="SELECT FILTER", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(pady=(10, 2))
        
        self.filter_choice = ctk.StringVar(value="None")
        self.filter_choice_menu = ctk.CTkOptionMenu(
            choice_frame,
            variable=self.filter_choice,
            values=["None", "Gaussian Blur", "Median Filter", "Sobel Edges", "Laplacian Edges"],
            command=self.on_filter_changed,
            height=28,
            fg_color="#444",
            button_color="#555",
            button_hover_color="#666"
        )
        self.filter_choice_menu.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(choice_frame, text="Selecione um filtro para ajustar suas propriedades e aplicar na imagem.", font=ctk.CTkFont(size=8, style="italic"), text_color="#888", wraplength=220, justify="left").pack(anchor="w", padx=10, pady=(0, 10))

        # Dynamic parameter frames container
        self.filter_params_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.filter_params_frame.pack(fill="x", pady=5)
        
        # 1. Gaussian Blur Parameters Frame
        self.frame_param_gaussian = ctk.CTkFrame(self.filter_params_frame, fg_color="#242424", corner_radius=8, border_width=1, border_color="#3a3a3a")
        ctk.CTkLabel(self.frame_param_gaussian, text="GAUSSIAN BLUR PARAMETERS", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(pady=(8, 2))
        
        # Kernel size
        fs_g_k = ctk.CTkFrame(self.frame_param_gaussian, fg_color="transparent")
        fs_g_k.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(fs_g_k, text="Kernel Size (Odd):", font=ctk.CTkFont(size=9), text_color="#aaa").pack(side="left")
        self.val_filter_gauss_k = ctk.CTkLabel(fs_g_k, text="5", font=ctk.CTkFont(size=9), text_color="#3d85c6")
        self.val_filter_gauss_k.pack(side="right")
        self.slider_filter_gauss_k = ctk.CTkSlider(self.frame_param_gaussian, from_=1, to=21, number_of_steps=10, command=self.on_filter_param_change, progress_color="#3d85c6", button_color="#3d85c6", button_hover_color="#2966a3")
        self.slider_filter_gauss_k.set(5)
        self.slider_filter_gauss_k.pack(fill="x", padx=10, pady=(0, 5))
        
        # Sigma
        fs_g_s = ctk.CTkFrame(self.frame_param_gaussian, fg_color="transparent")
        fs_g_s.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(fs_g_s, text="Sigma (Std Dev):", font=ctk.CTkFont(size=9), text_color="#aaa").pack(side="left")
        self.val_filter_gauss_s = ctk.CTkLabel(fs_g_s, text="1.0", font=ctk.CTkFont(size=9), text_color="#3d85c6")
        self.val_filter_gauss_s.pack(side="right")
        self.slider_filter_gauss_s = ctk.CTkSlider(self.frame_param_gaussian, from_=0.1, to=10.0, command=self.on_filter_param_change, progress_color="#3d85c6", button_color="#3d85c6", button_hover_color="#2966a3")
        self.slider_filter_gauss_s.set(1.0)
        self.slider_filter_gauss_s.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(self.frame_param_gaussian, text="Aplica uma suavização gaussiana. Ideal para redução de ruído genérico.", font=ctk.CTkFont(size=8, style="italic"), text_color="#888", wraplength=220, justify="left").pack(anchor="w", padx=10, pady=(0, 10))
        
        # 2. Median Blur Parameters Frame
        self.frame_param_median = ctk.CTkFrame(self.filter_params_frame, fg_color="#242424", corner_radius=8, border_width=1, border_color="#3a3a3a")
        ctk.CTkLabel(self.frame_param_median, text="MEDIAN FILTER PARAMETERS", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(pady=(8, 2))
        
        # Kernel size
        fs_m_k = ctk.CTkFrame(self.frame_param_median, fg_color="transparent")
        fs_m_k.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(fs_m_k, text="Kernel Size (Odd):", font=ctk.CTkFont(size=9), text_color="#aaa").pack(side="left")
        self.val_filter_median_k = ctk.CTkLabel(fs_m_k, text="5", font=ctk.CTkFont(size=9), text_color="#3d85c6")
        self.val_filter_median_k.pack(side="right")
        self.slider_filter_median_k = ctk.CTkSlider(self.frame_param_median, from_=1, to=21, number_of_steps=10, command=self.on_filter_param_change, progress_color="#3d85c6", button_color="#3d85c6", button_hover_color="#2966a3")
        self.slider_filter_median_k.set(5)
        self.slider_filter_median_k.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(self.frame_param_median, text="Filtro de mediana. Excelente para remoção de ruídos tipo sal e pimenta.", font=ctk.CTkFont(size=8, style="italic"), text_color="#888", wraplength=220, justify="left").pack(anchor="w", padx=10, pady=(0, 10))
        
        # 3. Sobel Parameters Frame
        self.frame_param_sobel = ctk.CTkFrame(self.filter_params_frame, fg_color="#242424", corner_radius=8, border_width=1, border_color="#3a3a3a")
        ctk.CTkLabel(self.frame_param_sobel, text="SOBEL EDGES PARAMETERS", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(pady=(8, 2))
        
        # Direction
        ctk.CTkLabel(self.frame_param_sobel, text="Direction:", font=ctk.CTkFont(size=9), text_color="#aaa").pack(anchor="w", padx=10)
        self.sobel_direction = ctk.StringVar(value="Combined")
        self.opt_sobel_direction = ctk.CTkOptionMenu(
            self.frame_param_sobel,
            variable=self.sobel_direction,
            values=["Combined", "Horizontal", "Vertical"],
            command=self.on_filter_param_change,
            height=25,
            fg_color="#444",
            button_color="#555",
            button_hover_color="#666"
        )
        self.opt_sobel_direction.pack(fill="x", padx=10, pady=(2, 8))
        
        # Kernel size
        fs_s_k = ctk.CTkFrame(self.frame_param_sobel, fg_color="transparent")
        fs_s_k.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(fs_s_k, text="Kernel Size (Odd):", font=ctk.CTkFont(size=9), text_color="#aaa").pack(side="left")
        self.val_filter_sobel_k = ctk.CTkLabel(fs_s_k, text="3", font=ctk.CTkFont(size=9), text_color="#3d85c6")
        self.val_filter_sobel_k.pack(side="right")
        self.slider_filter_sobel_k = ctk.CTkSlider(self.frame_param_sobel, from_=1, to=7, number_of_steps=3, command=self.on_filter_param_change, progress_color="#3d85c6", button_color="#3d85c6", button_hover_color="#2966a3")
        self.slider_filter_sobel_k.set(3)
        self.slider_filter_sobel_k.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(self.frame_param_sobel, text="Destaca gradientes e transições de intensidade. Útil para detecção de bordas orientadas.", font=ctk.CTkFont(size=8, style="italic"), text_color="#888", wraplength=220, justify="left").pack(anchor="w", padx=10, pady=(0, 10))

        # 4. Laplacian Parameters Frame
        self.frame_param_laplacian = ctk.CTkFrame(self.filter_params_frame, fg_color="#242424", corner_radius=8, border_width=1, border_color="#3a3a3a")
        ctk.CTkLabel(self.frame_param_laplacian, text="LAPLACIAN EDGES PARAMETERS", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(pady=(8, 2))
        
        # Kernel size
        fs_l_k = ctk.CTkFrame(self.frame_param_laplacian, fg_color="transparent")
        fs_l_k.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(fs_l_k, text="Kernel Size (Odd):", font=ctk.CTkFont(size=9), text_color="#aaa").pack(side="left")
        self.val_filter_laplacian_k = ctk.CTkLabel(fs_l_k, text="3", font=ctk.CTkFont(size=9), text_color="#3d85c6")
        self.val_filter_laplacian_k.pack(side="right")
        self.slider_filter_laplacian_k = ctk.CTkSlider(self.frame_param_laplacian, from_=1, to=7, number_of_steps=3, command=self.on_filter_param_change, progress_color="#3d85c6", button_color="#3d85c6", button_hover_color="#2966a3")
        self.slider_filter_laplacian_k.set(3)
        self.slider_filter_laplacian_k.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(self.frame_param_laplacian, text="Realça contornos usando a segunda derivada. Destaca todas as direções igualmente.", font=ctk.CTkFont(size=8, style="italic"), text_color="#888", wraplength=220, justify="left").pack(anchor="w", padx=10, pady=(0, 10))

        # Action Frame
        self.frame_filter_action = ctk.CTkFrame(scroll, fg_color="#242424", corner_radius=8, border_width=1, border_color="#3a3a3a")
        self.frame_filter_action.pack(fill="x", pady=10, padx=5)
        
        self.filter_preview_enabled = ctk.BooleanVar(value=True)
        self.check_filter_preview = ctk.CTkCheckBox(
            self.frame_filter_action,
            text="LIVE PREVIEW",
            font=ctk.CTkFont(size=10, weight="bold"),
            variable=self.filter_preview_enabled,
            command=self.apply_filters_live,
            checkbox_width=18,
            checkbox_height=18
        )
        self.check_filter_preview.pack(fill="x", padx=15, pady=(15, 5))
        
        self.btn_commit_filter = ctk.CTkButton(
            self.frame_filter_action,
            text="COMMIT FILTER",
            command=self.commit_filter_action,
            height=30,
            fg_color="#3d85c6",
            hover_color="#2966a3",
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.btn_commit_filter.pack(fill="x", padx=15, pady=(5, 15))

        self.on_filter_changed("None")

    def on_filter_changed(self, choice):
        self.frame_param_gaussian.pack_forget()
        self.frame_param_median.pack_forget()
        self.frame_param_sobel.pack_forget()
        self.frame_param_laplacian.pack_forget()
        
        if choice == "Gaussian Blur":
            self.frame_param_gaussian.pack(fill="x", pady=5, padx=5)
        elif choice == "Median Filter":
            self.frame_param_median.pack(fill="x", pady=5, padx=5)
        elif choice == "Sobel Edges":
            self.frame_param_sobel.pack(fill="x", pady=5, padx=5)
        elif choice == "Laplacian Edges":
            self.frame_param_laplacian.pack(fill="x", pady=5, padx=5)
            
        self.apply_filters_live()

    def on_filter_param_change(self, _=None):
        gk = int(self.slider_filter_gauss_k.get())
        if gk % 2 == 0: gk += 1
        self.val_filter_gauss_k.configure(text=str(gk))
        self.val_filter_gauss_s.configure(text=f"{self.slider_filter_gauss_s.get():.1f}")
        
        mk = int(self.slider_filter_median_k.get())
        if mk % 2 == 0: mk += 1
        self.val_filter_median_k.configure(text=str(mk))
        
        sk = int(self.slider_filter_sobel_k.get())
        if sk % 2 == 0: sk += 1
        self.val_filter_sobel_k.configure(text=str(sk))
        
        lk = int(self.slider_filter_laplacian_k.get())
        if lk % 2 == 0: lk += 1
        self.val_filter_laplacian_k.configure(text=str(lk))
        
        self.apply_filters_live()

    def setup_color_tab_ps(self):
        scroll = ctk.CTkScrollableFrame(self.tab_color, fg_color="transparent"); scroll.pack(fill="both", expand=True)
        preset_frame = ctk.CTkFrame(scroll, fg_color="#333", corner_radius=8); preset_frame.pack(fill="x", pady=5, padx=5)
        ctk.CTkLabel(preset_frame, text="COLOR PRESETS", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(pady=8)
        for act in [('Grayscale', 'grayscale'), ('Invert Colors', 'invert'), ('Equalize Hist.', 'equalize')]:
            ctk.CTkButton(preset_frame, text=act[0], command=lambda a=act[1]: self.apply_direct(a), fg_color="#444", height=28).pack(pady=2, padx=10, fill="x")
        iso_frame = ctk.CTkFrame(scroll, fg_color="#333", corner_radius=8, border_width=1, border_color="#444"); iso_frame.pack(fill="x", pady=10, padx=5)
        ctk.CTkLabel(iso_frame, text="COLOR ISOLATION", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(pady=8)
        self.isolate_var = ctk.StringVar(value="None")
        self.isolate_mode = ctk.CTkOptionMenu(
            iso_frame,
            values=["None", "Red", "Green", "Blue", "Yellow", "Cyan", "Magenta"],
            command=lambda v: [self.isolate_var.set(v.lower()), self.apply_isolate_live()],
            height=26,
            fg_color="#444",
            button_color="#555",
            button_hover_color="#666"
        )
        self.isolate_mode.set("None")
        self.isolate_mode.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(iso_frame, text="COMMIT COLOR ISOLATION", command=self.commit_color_isolation, height=26, fg_color="#3d85c6", hover_color="#2966a3", font=ctk.CTkFont(size=10, weight="bold")).pack(fill="x", padx=10, pady=(0, 10))

    def setup_history_tab_ps(self):
        self.hist_canvas = ctk.CTkCanvas(self.tab_history, bg="#1a1a1a", height=150, highlightthickness=0); self.hist_canvas.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(self.tab_history, text="STEP HISTORY", font=ctk.CTkFont(size=10, weight="bold")).pack(pady=5)
        self.btn_undo = ctk.CTkButton(self.tab_history, text="↩ Undo Step", command=self.undo_action, state="disabled", fg_color="#444"); self.btn_undo.pack(pady=5, padx=10, fill="x")
        self.btn_redo = ctk.CTkButton(self.tab_history, text="↪ Redo Step", command=self.redo_action, state="disabled", fg_color="#444"); self.btn_redo.pack(pady=5, padx=10, fill="x")
        self.btn_reset = ctk.CTkButton(self.tab_history, text="Reset to Original", command=self.reset_image, state="disabled", fg_color="#8c3d3d"); self.btn_reset.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(self.tab_history, text="ASSETS / LAYERS", font=ctk.CTkFont(size=10, weight="bold")).pack(pady=(20, 5))
        self.image_gallery = ctk.CTkScrollableFrame(self.tab_history, height=300, fg_color="#222"); self.image_gallery.pack(fill="both", expand=True, padx=5, pady=5)

    def setup_canvas_area(self):
        self.canvas_area = ctk.CTkFrame(self.main_pane, fg_color="#121212", corner_radius=0)
        self.main_pane.add(self.canvas_area, minsize=400)
        self.main_pane.paneconfig(self.canvas_area, stretch="always")
        self.quick_bar = ctk.CTkFrame(self.canvas_area, height=40, fg_color="#2b2b2b", corner_radius=0); self.quick_bar.pack(side="top", fill="x")
        self.btn_quick_undo = ctk.CTkButton(self.quick_bar, text="↩", width=30, height=25, command=self.undo_action, fg_color="transparent")
        self.btn_quick_undo.pack(side="left", padx=(10, 2), pady=5)
        self.btn_quick_redo = ctk.CTkButton(self.quick_bar, text="↪", width=30, height=25, command=self.redo_action, fg_color="transparent")
        self.btn_quick_redo.pack(side="left", padx=2, pady=5)
        self.btn_quick_reset = ctk.CTkButton(self.quick_bar, text="RESET CANVAS", width=100, height=25, command=self.reset_image, fg_color="#8c3d3d", font=ctk.CTkFont(size=10, weight="bold"))
        self.btn_quick_reset.pack(side="left", padx=10, pady=5)
        self.canvas_tabs = ctk.CTkFrame(self.canvas_area, height=30, fg_color="#333", corner_radius=0); self.canvas_tabs.pack(side="top", fill="x")
        self.tab_label = ctk.CTkLabel(self.canvas_tabs, text="  no_document.psd @ 100% (RGB/8) *  ", font=ctk.CTkFont(size=11), fg_color="#2b2b2b"); self.tab_label.pack(side="left", fill="y", padx=2)
        self.image_container = ctk.CTkFrame(self.canvas_area, fg_color="transparent"); self.image_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create a horizontal PanedWindow inside image_container for the two canvases
        import tkinter as tk
        self.canvas_pane = tk.PanedWindow(self.image_container, orient="horizontal", bd=0, sashwidth=4, bg="#121212", opaqueresize=True)
        self.canvas_pane.pack(fill="both", expand=True)

        # Left Panel (Original)
        self.left_canvas_frame = ctk.CTkFrame(self.canvas_pane, fg_color="#1a1a1a", corner_radius=8, border_width=1, border_color="#2b2b2b")
        self.canvas_pane.add(self.left_canvas_frame, minsize=100)
        
        header_left = ctk.CTkFrame(self.left_canvas_frame, height=30, fg_color="#252525", corner_radius=4)
        header_left.pack(side="top", fill="x", padx=1, pady=1)
        ctk.CTkLabel(header_left, text="ORIGINAL IMAGE", font=ctk.CTkFont(size=10, weight="bold"), text_color="#888").pack(pady=4)
        
        self.original_canvas = ctk.CTkLabel(self.left_canvas_frame, text="", fg_color="#1a1a1a")
        self.original_canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Right Panel (Processed Preview)
        self.right_canvas_frame = ctk.CTkFrame(self.canvas_pane, fg_color="#1a1a1a", corner_radius=8, border_width=1, border_color="#3d85c6")
        self.canvas_pane.add(self.right_canvas_frame, minsize=100)
        
        header_right = ctk.CTkFrame(self.right_canvas_frame, height=30, fg_color="#2b2b2b", corner_radius=4)
        header_right.pack(side="top", fill="x", padx=1, pady=1)
        ctk.CTkLabel(header_right, text="EDIT PREVIEW / PROCESSED", font=ctk.CTkFont(size=10, weight="bold"), text_color="#3d85c6").pack(pady=4)
        
        self.processed_canvas = ctk.CTkLabel(self.right_canvas_frame, text="NO DOCUMENT OPEN", fg_color="#1a1a1a", font=ctk.CTkFont(size=14))
        self.processed_canvas.pack(fill="both", expand=True, padx=5, pady=5)

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
            self.update_history_buttons_state()
        except Exception as e: messagebox.showerror("Erro", f"Failed: {e}")

    def reset_ui_params(self):
        if hasattr(self, 'filter_choice'):
            self.filter_choice.set("None")
            self.filter_choice_menu.set("None")
            if hasattr(self, 'frame_param_gaussian'):
                self.frame_param_gaussian.pack_forget()
                self.frame_param_median.pack_forget()
                self.frame_param_sobel.pack_forget()
                self.frame_param_laplacian.pack_forget()
                self.slider_filter_gauss_k.set(5); self.val_filter_gauss_k.configure(text="5")
                self.slider_filter_gauss_s.set(1.0); self.val_filter_gauss_s.configure(text="1.0")
                self.slider_filter_median_k.set(5); self.val_filter_median_k.configure(text="5")
                self.sobel_direction.set("Combined")
                self.opt_sobel_direction.set("Combined")
                self.slider_filter_sobel_k.set(3); self.val_filter_sobel_k.configure(text="3")
                self.slider_filter_laplacian_k.set(3); self.val_filter_laplacian_k.configure(text="3")
        self.slider_bright.set(0); self.val_bright.configure(text="0")
        self.slider_contrast.set(0); self.val_contrast.configure(text="0")
        self.slider_bin.set(127); self.val_bin.configure(text="127"); self.bin_enabled.set(False)
        self.bin_method.set("Binary")
        self.opt_bin_method.set("Binary")
        self.slider_bin_block_size.set(11); self.val_bin_block_size.configure(text="11")
        self.slider_bin_c.set(2); self.val_bin_c.configure(text="2")
        self.slider_bin.configure(state="normal")
        self.frame_adaptive.pack_forget()
        
        self.isolate_mode.set("None"); self.isolate_var.set("None")
        
        # Reset Transforms
        self.slider_rotate.set(0); self.val_rotate.configure(text="0°")
        self.slider_scale.set(1.0); self.val_scale.configure(text="1.00x")
        self.rotate_keep_bounds.set(True)
        self.lock_aspect_ratio.set(True)
        
        if self.image_service.current_image is not None:
            h, w = self.image_service.current_image.shape[:2]
            self.entry_width.delete(0, "end")
            self.entry_width.insert(0, str(w))
            self.entry_height.delete(0, "end")
            self.entry_height.insert(0, str(h))

    def reset_image(self):
        if self.image_service.reset() is not None:
            self.reset_ui_params()
            self.update_displays()
            self.update_history_buttons_state()
            self.set_status("Document Reset")

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
        colors_map = {'b': '#0000ff', 'g': '#00ff00', 'r': '#ff0000', 'k': '#ffffff'}
        for hist_counts, col in hists:
            points = []
            for i, count in enumerate(hist_counts): points.append(((i / 255) * w, h - (count / max_val) * h))
            self.hist_canvas.create_line(points, fill=colors_map.get(col, '#ffffff'), width=1)

    def apply_filters_live(self, _=None):
        if self.image_service.current_image is None: return
        
        choice = self.filter_choice.get()
        if not self.filter_preview_enabled.get() or choice == "None":
            self.update_displays()
            return
            
        img = self.image_service.current_image.copy()
        
        if choice == "Gaussian Blur":
            gk = int(self.slider_filter_gauss_k.get())
            if gk % 2 == 0: gk += 1
            gs = self.slider_filter_gauss_s.get()
            img = apply_gaussian_blur(img, kernel_size=gk, sigma=gs)
        elif choice == "Median Filter":
            mk = int(self.slider_filter_median_k.get())
            if mk % 2 == 0: mk += 1
            img = apply_median_blur(img, kernel_size=mk)
        elif choice == "Sobel Edges":
            sk = int(self.slider_filter_sobel_k.get())
            if sk % 2 == 0: sk += 1
            mode_map = {"Horizontal": "horizontal", "Vertical": "vertical", "Combined": "both"}
            s_dir = mode_map.get(self.sobel_direction.get(), "both")
            img = apply_sobel(img, direction=s_dir, ksize=sk)
        elif choice == "Laplacian Edges":
            lk = int(self.slider_filter_laplacian_k.get())
            if lk % 2 == 0: lk += 1
            img = apply_laplacian(img, ksize=lk)
            
        self.update_displays(img)

    def commit_filter_action(self):
        if self.image_service.current_image is None: return
        choice = self.filter_choice.get()
        if choice == "None":
            messagebox.showinfo("Info", "No filter selected.")
            return
            
        img = self.image_service.current_image.copy()
        
        if choice == "Gaussian Blur":
            gk = int(self.slider_filter_gauss_k.get())
            if gk % 2 == 0: gk += 1
            gs = self.slider_filter_gauss_s.get()
            img = apply_gaussian_blur(img, kernel_size=gk, sigma=gs)
        elif choice == "Median Filter":
            mk = int(self.slider_filter_median_k.get())
            if mk % 2 == 0: mk += 1
            img = apply_median_blur(img, kernel_size=mk)
        elif choice == "Sobel Edges":
            sk = int(self.slider_filter_sobel_k.get())
            if sk % 2 == 0: sk += 1
            mode_map = {"Horizontal": "horizontal", "Vertical": "vertical", "Combined": "both"}
            s_dir = mode_map.get(self.sobel_direction.get(), "both")
            img = apply_sobel(img, direction=s_dir, ksize=sk)
        elif choice == "Laplacian Edges":
            lk = int(self.slider_filter_laplacian_k.get())
            if lk % 2 == 0: lk += 1
            img = apply_laplacian(img, ksize=lk)
            
        self.image_service.update_current_image(img)
        self.reset_ui_params()
        self.update_displays()
        self.update_history_buttons_state()
        self.set_status(f"Filter Applied: {choice}")

    def apply_filter_permanent(self, filter_type):
        if self.image_service.current_image is None: return
        img = self.image_service.current_image.copy()
        if filter_type == 'gaussian':
            gk = int(self.slider_filter_gauss_k.get())
            if gk % 2 == 0: gk += 1
            gs = self.slider_filter_gauss_s.get()
            img = apply_gaussian_blur(img, kernel_size=gk, sigma=gs)
        elif filter_type == 'median':
            mk = int(self.slider_filter_median_k.get())
            if mk % 2 == 0: mk += 1
            img = apply_median_blur(img, kernel_size=mk)
        elif filter_type == 'laplacian':
            lk = int(self.slider_filter_laplacian_k.get())
            if lk % 2 == 0: lk += 1
            img = apply_laplacian(img, ksize=lk)
        elif filter_type == 'sobel':
            sk = int(self.slider_filter_sobel_k.get())
            if sk % 2 == 0: sk += 1
            mode_map = {"Horizontal": "horizontal", "Vertical": "vertical", "Combined": "both"}
            s_dir = mode_map.get(self.sobel_direction.get(), "both")
            img = apply_sobel(img, direction=s_dir, ksize=sk)
        self.image_service.update_current_image(img)
        self.reset_ui_params()
        self.update_displays()
        self.update_history_buttons_state()
        self.set_status(f"Filter Applied: {filter_type}")

    def apply_trans_live(self, _=None):
        if self.image_service.current_image is None: return
        img = self.image_service.current_image.copy()
        img = apply_brightness_contrast(img, brightness=self.slider_bright.get(), contrast=self.slider_contrast.get())
        if self.bin_enabled.get():
            block_val = int(self.slider_bin_block_size.get())
            if block_val % 2 == 0:
                block_val += 1
            img = apply_binarization(
                img, 
                threshold=int(self.slider_bin.get()),
                method=self.bin_method.get(),
                block_size=block_val,
                c=int(self.slider_bin_c.get())
            )
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
        self.image_service.update_current_image(img)
        self.reset_ui_params()
        self.update_displays()
        self.update_history_buttons_state()
        self.set_status(f"Action: {action}")

    def commit_changes(self):
        if self.image_service.current_image is None: return
        img = self.image_service.current_image.copy()
        img = apply_brightness_contrast(img, brightness=self.slider_bright.get(), contrast=self.slider_contrast.get())
        if self.bin_enabled.get():
            block_val = int(self.slider_bin_block_size.get())
            if block_val % 2 == 0:
                block_val += 1
            img = apply_binarization(
                img, 
                threshold=int(self.slider_bin.get()),
                method=self.bin_method.get(),
                block_size=block_val,
                c=int(self.slider_bin_c.get())
            )
        self.image_service.update_current_image(img)
        self.reset_ui_params()
        self.update_displays()
        self.update_history_buttons_state()
        self.set_status("Adjustments Committed")

    def undo_action(self):
        if self.image_service.undo() is not None:
            self.reset_ui_params()
            self.update_displays()
            self.update_history_buttons_state()
            self.set_status("Step Reverted")

    def redo_action(self):
        if self.image_service.redo() is not None:
            self.reset_ui_params()
            self.update_displays()
            self.update_history_buttons_state()
            self.set_status("Step Redone")

    def on_bin_method_change(self, choice):
        if choice in ["Adaptive Mean", "Adaptive Gaussian"]:
            self.slider_bin.configure(state="disabled")
            self.frame_adaptive.pack(fill="x", padx=10, pady=(5, 15))
        elif choice == "Otsu":
            self.slider_bin.configure(state="disabled")
            self.frame_adaptive.pack_forget()
        else:
            self.slider_bin.configure(state="normal")
            self.frame_adaptive.pack_forget()
        self.apply_trans_live()

    def on_adaptive_param_change(self, _=None):
        block_val = int(self.slider_bin_block_size.get())
        if block_val % 2 == 0:
            block_val += 1
        self.val_bin_block_size.configure(text=str(block_val))
        
        c_val = int(self.slider_bin_c.get())
        self.val_bin_c.configure(text=str(c_val))
        
        self.apply_trans_live()

    def setup_transforms_tab_ps(self):
        scroll = ctk.CTkScrollableFrame(self.tab_transforms, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
        # --- ROTATION SECTION ---
        rot_frame = ctk.CTkFrame(scroll, fg_color="#333", corner_radius=8, border_width=1, border_color="#444")
        rot_frame.pack(fill="x", pady=5, padx=5)
        
        rot_header = ctk.CTkFrame(rot_frame, fg_color="transparent")
        rot_header.pack(fill="x", padx=10, pady=(8, 0))
        ctk.CTkLabel(rot_header, text="ROTATION", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(side="left")
        self.val_rotate = ctk.CTkLabel(rot_header, text="0°", font=ctk.CTkFont(size=10), text_color="#3d85c6")
        self.val_rotate.pack(side="right")
        
        self.slider_rotate = ctk.CTkSlider(rot_frame, from_=-180, to=180, command=self.apply_rotate_live)
        self.slider_rotate.set(0)
        self.slider_rotate.pack(fill="x", padx=10, pady=(5, 5))
        
        self.rotate_keep_bounds = ctk.BooleanVar(value=True)
        self.check_keep_bounds = ctk.CTkCheckBox(
            rot_frame, 
            text="Adjust Canvas to Fit", 
            font=ctk.CTkFont(size=9), 
            variable=self.rotate_keep_bounds,
            command=self.apply_rotate_live,
            checkbox_width=16,
            checkbox_height=16
        )
        self.check_keep_bounds.pack(anchor="w", padx=10, pady=(0, 10))
        
        quick_btn_frame = ctk.CTkFrame(rot_frame, fg_color="transparent")
        quick_btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(quick_btn_frame, text="-90°", width=50, height=24, command=lambda: self.quick_rotate(-90), font=ctk.CTkFont(size=9)).pack(side="left", expand=True, padx=2)
        ctk.CTkButton(quick_btn_frame, text="90°", width=50, height=24, command=lambda: self.quick_rotate(90), font=ctk.CTkFont(size=9)).pack(side="left", expand=True, padx=2)
        ctk.CTkButton(quick_btn_frame, text="180°", width=50, height=24, command=lambda: self.quick_rotate(180), font=ctk.CTkFont(size=9)).pack(side="left", expand=True, padx=2)
        
        ctk.CTkButton(rot_frame, text="COMMIT ROTATION", command=self.commit_rotation, height=26, fg_color="#444", font=ctk.CTkFont(size=10, weight="bold")).pack(fill="x", padx=10, pady=(0, 10))
        
        # --- SCALE SECTION ---
        scale_frame = ctk.CTkFrame(scroll, fg_color="#333", corner_radius=8, border_width=1, border_color="#444")
        scale_frame.pack(fill="x", pady=5, padx=5)
        
        scale_header = ctk.CTkFrame(scale_frame, fg_color="transparent")
        scale_header.pack(fill="x", padx=10, pady=(8, 0))
        ctk.CTkLabel(scale_header, text="SCALE", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(side="left")
        self.val_scale = ctk.CTkLabel(scale_header, text="1.0x", font=ctk.CTkFont(size=10), text_color="#3d85c6")
        self.val_scale.pack(side="right")
        
        self.slider_scale = ctk.CTkSlider(scale_frame, from_=0.1, to=3.0, command=self.apply_scale_live)
        self.slider_scale.set(1.0)
        self.slider_scale.pack(fill="x", padx=10, pady=(5, 10))
        
        ctk.CTkButton(scale_frame, text="COMMIT SCALE", command=self.commit_scale, height=26, fg_color="#444", font=ctk.CTkFont(size=10, weight="bold")).pack(fill="x", padx=10, pady=(0, 10))
        
        # --- RESIZE SECTION ---
        resize_frame = ctk.CTkFrame(scroll, fg_color="#333", corner_radius=8, border_width=1, border_color="#444")
        resize_frame.pack(fill="x", pady=5, padx=5)
        
        resize_header = ctk.CTkFrame(resize_frame, fg_color="transparent")
        resize_header.pack(fill="x", padx=10, pady=(8, 5))
        ctk.CTkLabel(resize_header, text="RESIZE (PIXELS)", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(side="left")
        
        dim_frame = ctk.CTkFrame(resize_frame, fg_color="transparent")
        dim_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(dim_frame, text="W:", font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        self.entry_width = ctk.CTkEntry(dim_frame, width=70, height=24, font=ctk.CTkFont(size=10))
        self.entry_width.pack(side="left", padx=2)
        self.entry_width.bind("<KeyRelease>", self.on_width_changed)
        
        ctk.CTkLabel(dim_frame, text="H:", font=ctk.CTkFont(size=10)).pack(side="left", padx=10)
        self.entry_height = ctk.CTkEntry(dim_frame, width=70, height=24, font=ctk.CTkFont(size=10))
        self.entry_height.pack(side="left", padx=2)
        self.entry_height.bind("<KeyRelease>", self.on_height_changed)
        
        self.lock_aspect_ratio = ctk.BooleanVar(value=True)
        self.check_lock_aspect = ctk.CTkCheckBox(
            resize_frame, 
            text="Constrain Proportions", 
            font=ctk.CTkFont(size=9), 
            variable=self.lock_aspect_ratio,
            checkbox_width=16,
            checkbox_height=16
        )
        self.check_lock_aspect.pack(anchor="w", padx=10, pady=(5, 10))
        
        ctk.CTkButton(resize_frame, text="APPLY RESIZE", command=self.commit_resize, height=26, fg_color="#3d85c6", hover_color="#2966a3", font=ctk.CTkFont(size=10, weight="bold")).pack(fill="x", padx=10, pady=(0, 10))

    def on_width_changed(self, event=None):
        if not self.lock_aspect_ratio.get() or self.image_service.current_image is None:
            return
        try:
            val = self.entry_width.get()
            if not val:
                return
            w = int(val)
            h_orig, w_orig = self.image_service.current_image.shape[:2]
            aspect = h_orig / w_orig
            new_h = int(w * aspect)
            
            self.entry_height.delete(0, "end")
            self.entry_height.insert(0, str(new_h))
        except ValueError:
            pass

    def on_height_changed(self, event=None):
        if not self.lock_aspect_ratio.get() or self.image_service.current_image is None:
            return
        try:
            val = self.entry_height.get()
            if not val:
                return
            h = int(val)
            h_orig, w_orig = self.image_service.current_image.shape[:2]
            aspect = w_orig / h_orig
            new_w = int(h * aspect)
            
            self.entry_width.delete(0, "end")
            self.entry_width.insert(0, str(new_w))
        except ValueError:
            pass

    def apply_rotate_live(self, _=None):
        if self.image_service.current_image is None: return
        angle = self.slider_rotate.get()
        self.val_rotate.configure(text=f"{int(angle)}°")
        img = apply_rotation(self.image_service.current_image, angle, keep_bounds=self.rotate_keep_bounds.get())
        self.update_displays(img)

    def quick_rotate(self, angle):
        if self.image_service.current_image is None: return
        img = apply_rotation(self.image_service.current_image, angle, keep_bounds=self.rotate_keep_bounds.get())
        self.image_service.update_current_image(img)
        self.update_displays()
        self.reset_ui_params()
        self.update_history_buttons_state()
        self.set_status(f"Rotated by {angle}°")

    def commit_rotation(self):
        if self.image_service.current_image is None: return
        angle = self.slider_rotate.get()
        if angle == 0: return
        img = apply_rotation(self.image_service.current_image, angle, keep_bounds=self.rotate_keep_bounds.get())
        self.image_service.update_current_image(img)
        self.update_displays()
        self.reset_ui_params()
        self.update_history_buttons_state()
        self.set_status(f"Rotation Committed ({int(angle)}°)")

    def apply_scale_live(self, _=None):
        if self.image_service.current_image is None: return
        scale_val = self.slider_scale.get()
        self.val_scale.configure(text=f"{scale_val:.2f}x")
        img = apply_scale(self.image_service.current_image, scale_val)
        self.update_displays(img)

    def commit_scale(self):
        if self.image_service.current_image is None: return
        scale_val = self.slider_scale.get()
        if scale_val == 1.0: return
        img = apply_scale(self.image_service.current_image, scale_val)
        self.image_service.update_current_image(img)
        self.update_displays()
        self.reset_ui_params()
        self.update_history_buttons_state()
        self.set_status(f"Scale Committed ({scale_val:.2f}x)")

    def commit_resize(self):
        if self.image_service.current_image is None: return
        try:
            w = int(self.entry_width.get())
            h = int(self.entry_height.get())
            if w <= 0 or h <= 0:
                raise ValueError
            img = apply_resize(self.image_service.current_image, w, h)
            self.image_service.update_current_image(img)
            self.update_displays()
            self.reset_ui_params()
            self.update_history_buttons_state()
            self.set_status(f"Resized to {w}x{h}")
        except ValueError:
            messagebox.showerror("Error", "Invalid Width/Height dimensions.")

    def commit_color_isolation(self):
        if self.image_service.current_image is None: return
        color_choice = self.isolate_var.get()
        if color_choice == "None": return
        img = apply_isolate_color(self.image_service.current_image, color_choice)
        self.image_service.update_current_image(img)
        self.update_displays()
        self.reset_ui_params()
        self.update_history_buttons_state()
        self.set_status(f"Color Isolation Committed: {color_choice}")

    def update_history_buttons_state(self):
        if self.image_service.original_image is None:
            state_undo = "disabled"
            state_redo = "disabled"
            state_reset = "disabled"
        else:
            state_undo = "normal" if self.image_service.history_index > 0 else "disabled"
            state_redo = "normal" if self.image_service.history_index < len(self.image_service.history) - 1 else "disabled"
            state_reset = "normal" if self.image_service.history_index > 0 else "disabled"

        # Update sidebar history buttons
        self.btn_undo.configure(state=state_undo)
        self.btn_redo.configure(state=state_redo)
        self.btn_reset.configure(state=state_reset)
        
        # Update canvas quick bar buttons
        self.btn_quick_undo.configure(state=state_undo)
        self.btn_quick_redo.configure(state=state_redo)
        self.btn_quick_reset.configure(state=state_reset)

if __name__ == "__main__":
    app = ImageApp(); app.mainloop()
