import customtkinter as ctk

class HistoryTab(ctk.CTkFrame):
    def __init__(self, master, app):
        """
        Aba de Histórico (Histograma de intensidade, botões Undo/Redo/Reset e Galeria de presets).
        
        Parâmetros:
            master: Widget pai.
            app: Instância de ImageApp.
        """
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        # Canvas do Histograma
        self.hist_canvas = ctk.CTkCanvas(self, bg="#1a1a1a", height=150, highlightthickness=0)
        self.hist_canvas.pack(fill="x", padx=10, pady=10)
        self.hist_canvas.bind("<Configure>", lambda e: self.app.redraw_histogram())
        
        ctk.CTkLabel(self, text="STEP HISTORY", font=ctk.CTkFont(size=10, weight="bold")).pack(pady=5)
        
        # Botões de Ação do Histórico
        self.btn_undo = ctk.CTkButton(
            self, text="↩ Undo Step", command=self.app.controller.undo_action, 
            state="disabled", fg_color="#444"
        )
        self.btn_undo.pack(pady=5, padx=10, fill="x")
        
        self.btn_redo = ctk.CTkButton(
            self, text="↪ Redo Step", command=self.app.controller.redo_action, 
            state="disabled", fg_color="#444"
        )
        self.btn_redo.pack(pady=5, padx=10, fill="x")
        
        self.btn_reset = ctk.CTkButton(
            self, text="Reset to Original", command=self.app.controller.reset_image, 
            state="disabled", fg_color="#8c3d3d"
        )
        self.btn_reset.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(self, text="ASSETS / LAYERS", font=ctk.CTkFont(size=10, weight="bold")).pack(pady=(20, 5))
        
        # Galeria de fotos / ativos pré-carregados
        self.image_gallery = ctk.CTkScrollableFrame(self, height=300, fg_color="#222")
        self.image_gallery.pack(fill="both", expand=True, padx=5, pady=5)

    def set_history_states(self, has_undo: bool, has_redo: bool):
        """Atualiza a ativação dos botões de acordo com o estado do histórico."""
        state_undo = "normal" if has_undo else "disabled"
        state_redo = "normal" if has_redo else "disabled"
        state_reset = "normal" if has_undo else "disabled"
        
        self.btn_undo.configure(state=state_undo)
        self.btn_redo.configure(state=state_redo)
        self.btn_reset.configure(state=state_reset)

    # APIs públicas para recuperação do estado interno
    def get_histogram_canvas(self) -> ctk.CTkCanvas:
        return self.hist_canvas

    def get_gallery(self) -> ctk.CTkScrollableFrame:
        return self.image_gallery
