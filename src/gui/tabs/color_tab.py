import customtkinter as ctk

class ColorTab(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        """
        Aba de Cores (Presets rápidos e Isolamento cromático).
        
        Parâmetros:
            master: Widget pai.
            app: Instância de ImageApp.
        """
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        # Frame de Presets Rápidos
        preset_frame = ctk.CTkFrame(self, fg_color="#333", corner_radius=8)
        preset_frame.pack(fill="x", pady=5, padx=5)
        
        ctk.CTkLabel(preset_frame, text="COLOR PRESETS", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(pady=8)
        
        presets = [
            ('Grayscale', 'grayscale'), 
            ('Invert Colors', 'invert'), 
            ('Equalize Hist.', 'equalize')
        ]
        for name, action in presets:
            ctk.CTkButton(
                preset_frame, text=name, 
                command=lambda a=action: self.app.controller.apply_direct(a), 
                fg_color="#444", height=28
            ).pack(pady=2, padx=10, fill="x")

        # Frame de Isolamento Cromático
        iso_frame = ctk.CTkFrame(self, fg_color="#333", corner_radius=8, border_width=1, border_color="#444")
        iso_frame.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(iso_frame, text="COLOR ISOLATION", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(pady=8)
        
        self.isolate_var = ctk.StringVar(value="None")
        self.isolate_mode = ctk.CTkOptionMenu(
            iso_frame,
            values=["None", "Red", "Green", "Blue", "Yellow", "Cyan", "Magenta"],
            command=self.on_isolate_change,
            height=26,
            fg_color="#444",
            button_color="#555",
            button_hover_color="#666"
        )
        self.isolate_mode.set("None")
        self.isolate_mode.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            iso_frame, text="COMMIT COLOR ISOLATION", command=self.app.controller.commit_color_isolation, 
            height=26, fg_color="#3d85c6", hover_color="#2966a3", 
            font=ctk.CTkFont(size=10, weight="bold")
        ).pack(fill="x", padx=10, pady=(0, 10))

    def on_isolate_change(self, choice):
        self.isolate_var.set(choice.lower())
        self.app.controller.apply_isolate_live()

    # APIs públicas para recuperação do estado interno
    def get_isolate_color(self) -> str:
        return self.isolate_var.get()

    def reset_ui(self):
        self.isolate_mode.set("None")
        self.isolate_var.set("none")
