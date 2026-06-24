import customtkinter as ctk
import tkinter as tk

class CanvasArea(ctk.CTkFrame):
    def __init__(self, master, app):
        """
        Inicializa a área de exibição da imagem com dois painéis lado a lado (Original e Processado).
        
        Parâmetros:
            master: Widget pai.
            app: Instância de ImageApp que contém callbacks globais.
        """
        super().__init__(master, fg_color="#121212", corner_radius=0)
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        # Barra rápida (Quick Bar) com Undo/Redo/Reset
        self.quick_bar = ctk.CTkFrame(self, height=40, fg_color="#2b2b2b", corner_radius=0)
        self.quick_bar.pack(side="top", fill="x")
        
        self.btn_quick_undo = ctk.CTkButton(
            self.quick_bar, text="↩", width=30, height=25, 
            command=self.app.controller.undo_action, fg_color="transparent"
        )
        self.btn_quick_undo.pack(side="left", padx=(10, 2), pady=5)
        
        self.btn_quick_redo = ctk.CTkButton(
            self.quick_bar, text="↪", width=30, height=25, 
            command=self.app.controller.redo_action, fg_color="transparent"
        )
        self.btn_quick_redo.pack(side="left", padx=2, pady=5)
        
        self.btn_quick_reset = ctk.CTkButton(
            self.quick_bar, text="RESET CANVAS", width=100, height=25, 
            command=self.app.controller.reset_image, fg_color="#8c3d3d", 
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.btn_quick_reset.pack(side="left", padx=10, pady=5)

        # Abas de navegação fictícias do documento
        self.canvas_tabs = ctk.CTkFrame(self, height=30, fg_color="#333", corner_radius=0)
        self.canvas_tabs.pack(side="top", fill="x")
        
        self.tab_label = ctk.CTkLabel(
            self.canvas_tabs, text="  no_document.psd @ 100% (RGB/8) *  ", 
            font=ctk.CTkFont(size=11), fg_color="#2b2b2b"
        )
        self.tab_label.pack(side="left", fill="y", padx=2)

        # Container dos painéis de imagem
        self.image_container = ctk.CTkFrame(self, fg_color="transparent")
        self.image_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # PanedWindow para dividir o espaço igualmente em 50% para cada visualização
        self.canvas_pane = tk.PanedWindow(self.image_container, orient="horizontal", bd=0, sashwidth=4, bg="#121212", opaqueresize=True)
        self.canvas_pane.pack(fill="both", expand=True)

        # Painel Esquerdo (Imagem Original)
        self.left_canvas_frame = ctk.CTkFrame(self.canvas_pane, fg_color="#1a1a1a", corner_radius=8, border_width=1, border_color="#2b2b2b")
        self.canvas_pane.add(self.left_canvas_frame, minsize=100, width=1, stretch="always")
        
        header_left = ctk.CTkFrame(self.left_canvas_frame, height=30, fg_color="#252525", corner_radius=4)
        header_left.pack(side="top", fill="x", padx=1, pady=1)
        ctk.CTkLabel(header_left, text="ORIGINAL IMAGE", font=ctk.CTkFont(size=10, weight="bold"), text_color="#888").pack(pady=4)
        
        self.original_canvas = ctk.CTkLabel(self.left_canvas_frame, text="", fg_color="#1a1a1a")
        self.original_canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Painel Direito (Pré-visualização do Processamento)
        self.right_canvas_frame = ctk.CTkFrame(self.canvas_pane, fg_color="#1a1a1a", corner_radius=8, border_width=1, border_color="#3d85c6")
        self.canvas_pane.add(self.right_canvas_frame, minsize=100, width=1, stretch="always")
        
        header_right = ctk.CTkFrame(self.right_canvas_frame, height=30, fg_color="#2b2b2b", corner_radius=4)
        header_right.pack(side="top", fill="x", padx=1, pady=1)
        ctk.CTkLabel(header_right, text="EDIT PREVIEW / PROCESSED", font=ctk.CTkFont(size=10, weight="bold"), text_color="#3d85c6").pack(pady=4)
        
        self.processed_canvas = ctk.CTkLabel(self.right_canvas_frame, text="NO DOCUMENT OPEN", fg_color="#1a1a1a", font=ctk.CTkFont(size=14))
        self.processed_canvas.pack(fill="both", expand=True, padx=5, pady=5)

    def set_tab_label(self, text: str):
        """Atualiza a indicação do documento ativo."""
        self.tab_label.configure(text=text)

    def set_history_states(self, has_undo: bool, has_redo: bool):
        """Ativa ou desativa os botões da barra rápida conforme o estado da pilha de Undo/Redo."""
        state_undo = "normal" if has_undo else "disabled"
        state_redo = "normal" if has_redo else "disabled"
        state_reset = "normal" if has_undo else "disabled"
        
        self.btn_quick_undo.configure(state=state_undo)
        self.btn_quick_redo.configure(state=state_redo)
        self.btn_quick_reset.configure(state=state_reset)
