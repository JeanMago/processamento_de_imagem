import customtkinter as ctk
import tkinter as tk
from ..services.image_service import ImageService
from ..utils.utils import cv2_to_pil, resize_to_fit, calculate_histogram

from .components import MenuBar, CanvasArea
from .tabs import AdjustTab, FiltersTab, ColorTab, TransformsTab, HistoryTab
from .controllers import ImageController

class ImageApp(ctk.CTk):
    def __init__(self):
        """
        Inicializa a View principal (ImageApp) do PhotoPro PDI.
        Configura os parâmetros da janela do Tkinter, instancia o Model (ImageService)
        e o Controller (ImageController) e realiza a montagem de layouts.
        """
        super().__init__()

        self.title("PDI PhotoPro - Advanced Image Editor")
        self.geometry("1600x1000")
        
        # Tema Escuro inspirado no Photoshop
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#1e1e1e")

        # Inicialização do Modelo e do Controlador
        self.image_service = ImageService()
        self.controller = ImageController(self, self.image_service)
        
        # Estados específicos de exibição/View
        self.current_file_path = None
        self.last_processed_preview = None
        self._resize_job = None
        self.zoom_level = 1.0
        
        # Montagem dos componentes visuais
        self.setup_ui_skeleton()
        self.setup_canvas_area()
        self.setup_properties_panel()
        self.controller.load_predefined_images()
        self.bind_events()

    def setup_ui_skeleton(self):
        """Configura a divisão de pesos do layout principal (Grid)."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        # Top Bar (Menus)
        self.menu_bar = MenuBar(self, self)
        self.menu_bar.grid(row=0, column=0, columnspan=2, sticky="new")

        # Barra de Status inferior
        self.status_bar = ctk.CTkFrame(self, height=25, corner_radius=0, fg_color="#2b2b2b", border_width=1, border_color="#1a1a1a")
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="sew")
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="Ready", font=ctk.CTkFont(size=11), text_color="#888")
        self.status_label.pack(side="left", padx=15)
        
        self.coords_label = ctk.CTkLabel(self.status_bar, text="X: 0, Y: 0", font=ctk.CTkFont(size=11), text_color="#888")
        self.coords_label.pack(side="right", padx=10)
        
        self.zoom_info_label = ctk.CTkLabel(self.status_bar, text="100% | RGB/8", font=ctk.CTkFont(size=11), text_color="#888")
        self.zoom_info_label.pack(side="right", padx=15)

    def setup_canvas_area(self):
        """Monta a região central de exibição das imagens com margens flutuantes elegantes."""
        self.canvas_area = CanvasArea(self, self)
        self.canvas_area.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        # Atalhos para os widgets internos expostos (retrocompatibilidade com o controller)
        self.original_canvas = self.canvas_area.original_canvas
        self.processed_canvas = self.canvas_area.processed_canvas
        self.left_canvas_frame = self.canvas_area.left_canvas_frame
        self.right_canvas_frame = self.canvas_area.right_canvas_frame

    def setup_properties_panel(self):
        """Monta a barra lateral direita de largura fixa e suas abas de controle de propriedades."""
        self.prop_panel = ctk.CTkFrame(self, width=420, corner_radius=8, fg_color="#252525", border_width=1, border_color="#1a1a1a")
        self.prop_panel.pack_propagate(False)
        self.prop_panel.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        self.prop_header = ctk.CTkFrame(self.prop_panel, height=40, fg_color="#333", corner_radius=0)
        self.prop_header.pack(fill="x")
        ctk.CTkLabel(self.prop_header, text="PROPERTIES & TOOLS", font=ctk.CTkFont(size=11, weight="bold"), text_color="#aaa").pack(pady=10)
        
        self.hud_panel = ctk.CTkTabview(self.prop_panel, fg_color="#2b2b2b", segmented_button_selected_color="#3d85c6")
        self.hud_panel._segmented_button.configure(font=ctk.CTkFont(size=9, weight="bold"))
        self.hud_panel.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        tab_adjust = self.hud_panel.add("☀️ ADJUST")
        tab_filters = self.hud_panel.add("✨ FILTERS")
        tab_color = self.hud_panel.add("🎨 COLOR")
        tab_transforms = self.hud_panel.add("📐 TRANSFORMS")
        tab_history = self.hud_panel.add("📜 HISTORY")
        
        # Instanciação das abas
        self.adjust_tab = AdjustTab(tab_adjust, self)
        self.adjust_tab.pack(fill="both", expand=True)
        
        self.filters_tab = FiltersTab(tab_filters, self)
        self.filters_tab.pack(fill="both", expand=True)
        
        self.color_tab = ColorTab(tab_color, self)
        self.color_tab.pack(fill="both", expand=True)
        
        self.transforms_tab = TransformsTab(tab_transforms, self)
        self.transforms_tab.pack(fill="both", expand=True)
        
        self.history_tab = HistoryTab(tab_history, self)
        self.history_tab.pack(fill="both", expand=True)
        
        # Exposição de atalhos requeridos pelo renderizador
        self.image_gallery = self.history_tab.get_gallery()
        self.hist_canvas = self.history_tab.get_histogram_canvas()

    def bind_events(self):
        """Aplica os binds de redimensionamento e interações sobre o Canvas."""
        self.processed_canvas.bind("<Motion>", self.track_mouse)
        self.processed_canvas.bind("<MouseWheel>", self.handle_zoom)
        self.left_canvas_frame.bind("<Configure>", self.on_canvas_resize)
        self.right_canvas_frame.bind("<Configure>", self.on_canvas_resize)

    def on_canvas_resize(self, event=None):
        if self.image_service.original_image is None: return
        if hasattr(self, '_resize_job') and self._resize_job is not None:
            try:
                self.after_cancel(self._resize_job)
            except Exception:
                pass
        self._resize_job = self.after(80, self._perform_canvas_resize)

    def _perform_canvas_resize(self):
        self._resize_job = None
        self.update_displays(is_resize=True)

    def track_mouse(self, event):
        self.coords_label.configure(text=f"X: {event.x}, Y: {event.y}")

    def handle_zoom(self, event):
        if event.delta > 0: self.controller.handle_view_menu("Zoom In")
        else: self.controller.handle_view_menu("Zoom Out")

    def toggle_properties_panel(self):
        """Controla a visibilidade (exibição/ocultação) do painel lateral de ferramentas de forma fixa e direta."""
        if self.prop_panel.winfo_manager() == "grid":
            self.prop_panel.grid_forget()
        else:
            self.prop_panel.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)
            self.update_label_wrapping()
            self.redraw_histogram()


    def update_label_wrapping(self):
        try:
            w = self.hud_panel.winfo_width() - 45
            self.filters_tab.update_layout(w)
        except Exception:
            pass

    def set_status(self, text: str):
        self.status_label.configure(text=text)

    def reset_ui_params(self):
        """Reseta todos os sliders e estados de abas de volta ao padrão."""
        self.last_processed_preview = None
        self.adjust_tab.reset_ui()
        self.filters_tab.reset_ui()
        self.color_tab.reset_ui()
        
        shape = self.image_service.current_image.shape[:2] if self.image_service.current_image is not None else None
        self.transforms_tab.reset_ui(shape)

    def update_displays(self, processed=None, is_resize=False):
        """Redimensiona e renderiza as imagens original e ativa nos canvases da tela."""
        if self.image_service.original_image is None: return
        
        if processed is not None:
            self.last_processed_preview = processed
            
        display_img = processed if processed is not None else (
            self.last_processed_preview if hasattr(self, 'last_processed_preview') and self.last_processed_preview is not None
            else self.image_service.current_image
        )
        
        w_avail = self.left_canvas_frame.winfo_width() - 10
        h_avail = self.left_canvas_frame.winfo_height() - 40
        
        if w_avail < 50: w_avail = 600
        if h_avail < 50: h_avail = 500
        
        w_scaled = int(w_avail * self.zoom_level)
        h_scaled = int(h_avail * self.zoom_level)
        
        orig_resized = resize_to_fit(self.image_service.original_image, w_scaled, h_scaled)
        pil_orig = cv2_to_pil(orig_resized)
        ctk_orig = ctk.CTkImage(light_image=pil_orig, dark_image=pil_orig, size=(pil_orig.width, pil_orig.height))
        self.original_canvas.configure(image=ctk_orig, text="")
        self.original_canvas._image = ctk_orig
        
        proc_resized = resize_to_fit(display_img, w_scaled, h_scaled)
        pil_proc = cv2_to_pil(proc_resized)
        ctk_proc = ctk.CTkImage(light_image=pil_proc, dark_image=pil_proc, size=(pil_proc.width, pil_proc.height))
        self.processed_canvas.configure(image=ctk_proc, text="")
        self.processed_canvas._image = ctk_proc
        
        if not is_resize:
            self.update_histogram(display_img)

    def update_histogram(self, image):
        """Desenha a distribuição de canais cromáticos no Canvas do Histograma."""
        self.last_hist_image = image
        self.hist_canvas.delete("all")
        
        w = self.hist_canvas.winfo_width()
        if w < 50:
            w = 220
        h = 150
        
        hists = calculate_histogram(image)
        max_val = max([h[0].max() for h in hists]) if hists else 1
        colors_map = {'b': '#0000ff', 'g': '#00ff00', 'r': '#ff0000', 'k': '#ffffff'}
        
        for hist_counts, col in hists:
            points = []
            for i, count in enumerate(hist_counts):
                points.append(((i / 255) * w, h - (count / max_val) * h))
            self.hist_canvas.create_line(points, fill=colors_map.get(col, '#ffffff'), width=1)

    def redraw_histogram(self):
        if hasattr(self, '_animating_prop') and self._animating_prop:
            return
        if hasattr(self, 'last_hist_image') and self.last_hist_image is not None:
            self.update_histogram(self.last_hist_image)

if __name__ == "__main__":
    app = ImageApp()
    app.mainloop()
