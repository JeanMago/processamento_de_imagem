import customtkinter as ctk
import cv2
import os
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np

from ...filters.filters import apply_gaussian_blur, apply_median_blur, apply_laplacian, apply_sobel
from ...transformations.transformations import (
    apply_brightness_contrast, apply_binarization, apply_invert_colors, 
    apply_grayscale, apply_isolate_color, apply_histogram_equalization,
    apply_resize, apply_rotation, apply_scale
)

class ImageController:
    def __init__(self, app, image_service):
        """
        Controlador principal de processamento de imagem (MVC).
        
        Gerencia o fluxo de controle entre a View (ImageApp) e o Model (ImageService),
        aplicando os filtros e transformações matemáticas sobre as imagens.
        
        Parâmetros:
            app: Instância do ImageApp (View).
            image_service: Instância do ImageService (Model).
        """
        self.app = app
        self.image_service = image_service

    # --- AÇÕES DE ARQUIVO E HISTÓRICO ---
    def handle_file_menu(self, choice: str):
        if choice == "Open...": self.open_image_dialog()
        elif choice == "Save": self.save_image_dialog()
        elif choice == "Exit": self.app.quit()

    def handle_edit_menu(self, choice: str):
        if choice == "Undo": self.undo_action()
        elif choice == "Redo": self.redo_action()
        elif choice == "Reset Image": self.reset_image()

    def handle_image_menu(self, choice: str):
        if choice == "Grayscale": self.apply_direct('grayscale')
        elif choice == "Invert": self.apply_direct('invert')
        elif choice == "Equalize": self.apply_direct('equalize')

    def handle_filter_menu(self, choice: str):
        if choice == "Gaussian Blur": self.apply_filter_permanent('gaussian')
        elif choice == "Median Filter": self.apply_filter_permanent('median')
        elif choice == "Sobel Edges": self.apply_filter_permanent('sobel')
        elif choice == "Laplacian": self.apply_filter_permanent('laplacian')

    def handle_view_menu(self, choice: str):
        if choice == "Zoom In": self.app.zoom_level *= 1.2
        elif choice == "Zoom Out": self.app.zoom_level /= 1.2
        elif choice == "Fit Screen": self.app.zoom_level = 1.0
        self.app.zoom_level = max(0.1, min(self.app.zoom_level, 5.0))
        self.app.zoom_info_label.configure(text=f"{int(self.app.zoom_level*100)}% | RGB/8")
        self.app.update_displays()

    def handle_window_menu(self, choice: str):
        if choice == "Toggle Properties":
            self.app.toggle_properties_panel()

    def load_predefined_images(self):
        """Carrega e renderiza a galeria de imagens pré-definidas da pasta 'images'."""
        img_folder = "images"
        if not os.path.exists(img_folder): return
        files = [f for f in os.listdir(img_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        for file in files:
            path = os.path.join(img_folder, file)
            try:
                img = Image.open(path); img.thumbnail((80, 80))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
                btn = ctk.CTkButton(
                    self.app.image_gallery, text=file, image=ctk_img, compound="top", 
                    command=lambda p=path: self.load_image(p), fg_color="#2b2b2b", font=ctk.CTkFont(size=10)
                )
                btn._image = ctk_img
                btn.pack(pady=5, padx=5, fill="x")
            except Exception as e:
                print(f"Thumbnail error: {e}")

    def load_image(self, path: str):
        """Carrega um arquivo de imagem no modelo (ImageService) e atualiza a interface."""
        try:
            self.image_service.load_image(path)
            self.app.current_file_path = path
            self.app.update_displays()
            self.update_history_buttons_state()
            self.app.set_status(f"Document Opened: {os.path.basename(path)}")
            self.app.canvas_area.set_tab_label(f"  {os.path.basename(path)} @ 100% (RGB/8) *  ")
            self.app.reset_ui_params()
        except Exception as e:
            messagebox.showerror("Erro", f"Failed to load image: {e}")

    def open_image_dialog(self):
        path = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.tiff")])
        if path: self.load_image(path)

    def save_image_dialog(self):
        if self.image_service.current_image is None: return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPG", "*.jpg")])
        if path and self.image_service.save_image(path):
            messagebox.showinfo("Success", "File Exported")
            self.app.set_status(f"Exported: {os.path.basename(path)}")

    def reset_image(self):
        """Restaura a imagem de volta ao seu estado original de carregamento."""
        if self.image_service.reset() is not None:
            self.app.reset_ui_params()
            self.app.update_displays()
            self.update_history_buttons_state()
            self.app.set_status("Document Reset")

    def undo_action(self):
        """Desfaz o último processamento de imagem gravado no histórico."""
        if self.image_service.undo() is not None:
            self.app.reset_ui_params()
            self.app.update_displays()
            self.update_history_buttons_state()
            self.app.set_status("Step Reverted")

    def redo_action(self):
        """Refaz o processamento desfeito na pilha de histórico."""
        if self.image_service.redo() is not None:
            self.app.reset_ui_params()
            self.app.update_displays()
            self.update_history_buttons_state()
            self.app.set_status("Step Redone")

    def update_history_buttons_state(self):
        """Ativa/Desativa botões de controle de Undo/Redo baseando-se nos buffers do modelo."""
        if self.image_service.original_image is None:
            has_undo = False
            has_redo = False
        else:
            has_undo = self.image_service.history_index > 0
            has_redo = self.image_service.history_index < len(self.image_service.history) - 1

        self.app.history_tab.set_history_states(has_undo, has_redo)
        self.app.canvas_area.set_history_states(has_undo, has_redo)

    # --- PROCESSADORES DE FILTROS ESPACIAIS ---
    def apply_filters_live(self, _=None):
        """Aplica filtros espaciais temporariamente em tempo de execução (pré-visualização)."""
        if self.image_service.current_image is None: return
        
        choice = self.app.filters_tab.get_filter_choice()
        if not self.app.filters_tab.is_preview_enabled() or choice == "None":
            self.app.update_displays()
            return
            
        img = self.image_service.current_image.copy()
        
        if choice == "Gaussian Blur":
            gk, gs = self.app.filters_tab.get_gaussian_params()
            img = apply_gaussian_blur(img, kernel_size=gk, sigma=gs)
        elif choice == "Median Filter":
            mk = self.app.filters_tab.get_median_params()
            img = apply_median_blur(img, kernel_size=mk)
        elif choice == "Sobel Edges":
            s_dir, sk = self.app.filters_tab.get_sobel_params()
            img = apply_sobel(img, direction=s_dir, ksize=sk)
        elif choice == "Laplacian Edges":
            lk = self.app.filters_tab.get_laplacian_params()
            img = apply_laplacian(img, ksize=lk)
            
        self.app.update_displays(img)

    def commit_filter_action(self):
        """Grava permanentemente o filtro ativo no histórico de imagens."""
        if self.image_service.current_image is None: return
        choice = self.app.filters_tab.get_filter_choice()
        if choice == "None":
            messagebox.showinfo("Info", "No filter selected.")
            return
            
        img = self.image_service.current_image.copy()
        
        if choice == "Gaussian Blur":
            gk, gs = self.app.filters_tab.get_gaussian_params()
            img = apply_gaussian_blur(img, kernel_size=gk, sigma=gs)
        elif choice == "Median Filter":
            mk = self.app.filters_tab.get_median_params()
            img = apply_median_blur(img, kernel_size=mk)
        elif choice == "Sobel Edges":
            s_dir, sk = self.app.filters_tab.get_sobel_params()
            img = apply_sobel(img, direction=s_dir, ksize=sk)
        elif choice == "Laplacian Edges":
            lk = self.app.filters_tab.get_laplacian_params()
            img = apply_laplacian(img, ksize=lk)
            
        self.image_service.update_current_image(img)
        self.app.reset_ui_params()
        self.app.update_displays()
        self.update_history_buttons_state()
        self.app.set_status(f"Filter Applied: {choice}")

    def apply_filter_permanent(self, filter_type: str):
        """Aplica um filtro imediatamente (a partir do menu) sem passar por live preview."""
        if self.image_service.current_image is None: return
        img = self.image_service.current_image.copy()
        if filter_type == 'gaussian':
            gk, gs = self.app.filters_tab.get_gaussian_params()
            img = apply_gaussian_blur(img, kernel_size=gk, sigma=gs)
        elif filter_type == 'median':
            mk = self.app.filters_tab.get_median_params()
            img = apply_median_blur(img, kernel_size=mk)
        elif filter_type == 'laplacian':
            lk = self.app.filters_tab.get_laplacian_params()
            img = apply_laplacian(img, ksize=lk)
        elif filter_type == 'sobel':
            s_dir, sk = self.app.filters_tab.get_sobel_params()
            img = apply_sobel(img, direction=s_dir, ksize=sk)
            
        self.image_service.update_current_image(img)
        self.app.reset_ui_params()
        self.app.update_displays()
        self.update_history_buttons_state()
        self.app.set_status(f"Filter Applied: {filter_type}")

    # --- PROCESSADORES DE AJUSTES E INTENSIDADE ---
    def apply_trans_live(self, _=None):
        """Atualiza a pré-visualização das transformações de Brilho, Contraste e Limiarização."""
        if self.image_service.current_image is None: return
        img = self.image_service.current_image.copy()
        img = apply_brightness_contrast(img, brightness=self.app.adjust_tab.get_brightness(), contrast=self.app.adjust_tab.get_contrast())
        if self.app.adjust_tab.is_bin_enabled():
            img = apply_binarization(
                img, 
                threshold=self.app.adjust_tab.get_bin_threshold(),
                method=self.app.adjust_tab.get_bin_method(),
                block_size=self.app.adjust_tab.get_bin_block_size(),
                c=self.app.adjust_tab.get_bin_c()
            )
        self.app.update_displays(img)

    def commit_changes(self):
        """Aplica em definitivo os ajustes de intensidade na pilha do histórico."""
        if self.image_service.current_image is None: return
        img = self.image_service.current_image.copy()
        img = apply_brightness_contrast(img, brightness=self.app.adjust_tab.get_brightness(), contrast=self.app.adjust_tab.get_contrast())
        if self.app.adjust_tab.is_bin_enabled():
            img = apply_binarization(
                img, 
                threshold=self.app.adjust_tab.get_bin_threshold(),
                method=self.app.adjust_tab.get_bin_method(),
                block_size=self.app.adjust_tab.get_bin_block_size(),
                c=self.app.adjust_tab.get_bin_c()
            )
        self.image_service.update_current_image(img)
        self.app.reset_ui_params()
        self.app.update_displays()
        self.update_history_buttons_state()
        self.app.set_status("Adjustments Committed")

    def apply_direct(self, action: str):
        """Aplica operações imediatas pontuais (Invert, Grayscale, Equalize) do menu ou presets."""
        if self.image_service.current_image is None: return
        if action == 'invert': img = apply_invert_colors(self.image_service.current_image)
        elif action == 'grayscale': img = apply_grayscale(self.image_service.current_image)
        elif action == 'equalize': img = apply_histogram_equalization(self.image_service.current_image)
        self.image_service.update_current_image(img)
        self.app.reset_ui_params()
        self.app.update_displays()
        self.update_history_buttons_state()
        self.app.set_status(f"Action: {action}")

    # --- PROCESSADORES DE ISOLAMENTO DE CORES ---
    def apply_isolate_live(self):
        if self.image_service.current_image is None: return
        color_choice = self.app.color_tab.get_isolate_color()
        if color_choice == "None": self.app.update_displays(); return
        img = apply_isolate_color(self.image_service.current_image, color_choice)
        self.app.update_displays(img)

    def commit_color_isolation(self):
        if self.image_service.current_image is None: return
        color_choice = self.app.color_tab.get_isolate_color()
        if color_choice == "None": return
        img = apply_isolate_color(self.image_service.current_image, color_choice)
        self.image_service.update_current_image(img)
        self.app.update_displays()
        self.app.reset_ui_params()
        self.update_history_buttons_state()
        self.app.set_status(f"Color Isolation Committed: {color_choice}")

    # --- PROCESSADORES GEOMÉTRICOS ---
    def apply_rotate_live(self, _=None):
        if self.image_service.current_image is None: return
        angle = self.app.transforms_tab.get_rotation_angle()
        img = apply_rotation(self.image_service.current_image, angle, keep_bounds=self.app.transforms_tab.get_keep_bounds())
        self.app.update_displays(img)

    def quick_rotate(self, angle: float):
        if self.image_service.current_image is None: return
        img = apply_rotation(self.image_service.current_image, angle, keep_bounds=self.app.transforms_tab.get_keep_bounds())
        self.image_service.update_current_image(img)
        self.app.update_displays()
        self.app.reset_ui_params()
        self.update_history_buttons_state()
        self.app.set_status(f"Rotated by {angle}°")

    def commit_rotation(self):
        if self.image_service.current_image is None: return
        angle = self.app.transforms_tab.get_rotation_angle()
        if angle == 0: return
        img = apply_rotation(self.image_service.current_image, angle, keep_bounds=self.app.transforms_tab.get_keep_bounds())
        self.image_service.update_current_image(img)
        self.app.update_displays()
        self.app.reset_ui_params()
        self.update_history_buttons_state()
        self.app.set_status(f"Rotation Committed ({int(angle)}°)")

    def apply_scale_live(self, _=None):
        if self.image_service.current_image is None: return
        scale_val = self.app.transforms_tab.get_scale()
        img = apply_scale(self.image_service.current_image, scale_val)
        self.app.update_displays(img)

    def commit_scale(self):
        if self.image_service.current_image is None: return
        scale_val = self.app.transforms_tab.get_scale()
        if scale_val == 1.0: return
        img = apply_scale(self.image_service.current_image, scale_val)
        self.image_service.update_current_image(img)
        self.app.update_displays()
        self.app.reset_ui_params()
        self.update_history_buttons_state()
        self.app.set_status(f"Scale Committed ({scale_val:.2f}x)")

    def commit_resize(self):
        if self.image_service.current_image is None: return
        try:
            w, h = self.app.transforms_tab.get_resize_dimensions()
            if w <= 0 or h <= 0:
                raise ValueError
            img = apply_resize(self.image_service.current_image, w, h)
            self.image_service.update_current_image(img)
            self.app.update_displays()
            self.app.reset_ui_params()
            self.update_history_buttons_state()
            self.app.set_status(f"Resized to {w}x{h}")
        except ValueError:
            messagebox.showerror("Error", "Invalid Width/Height dimensions.")
