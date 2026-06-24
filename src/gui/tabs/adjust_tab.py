import customtkinter as ctk

class AdjustTab(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        """
        Aba de Ajustes (Ajustes de Brilho, Contraste e Limiarização).
        
        Parâmetros:
            master: Widget pai.
            app: Instância de ImageApp que gerencia o estado e as transformações.
        """
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        # Grupo do Slider de Brilho
        self.slider_bright, self.val_bright = self.create_slider_group(
            self, "Brightness", -100, 100, 0, self.on_adjust_slider_change
        )
        
        # Grupo do Slider de Contraste
        self.slider_contrast, self.val_contrast = self.create_slider_group(
            self, "Contrast", -100, 100, 0, self.on_adjust_slider_change
        )
        
        # Painel de Limiarização (Thresholding)
        self.frame_bin_main = ctk.CTkFrame(self, fg_color="#333", corner_radius=8, border_width=1, border_color="#444")
        self.frame_bin_main.pack(fill="x", pady=10, padx=5)
        
        self.bin_header = ctk.CTkFrame(self.frame_bin_main, fg_color="transparent")
        self.bin_header.pack(fill="x", padx=10, pady=(10, 0))
        
        self.bin_enabled = ctk.BooleanVar(value=False)
        self.check_bin = ctk.CTkCheckBox(
            self.bin_header, text="THRESHOLDING", font=ctk.CTkFont(size=10, weight="bold"), 
            variable=self.bin_enabled, command=self.app.controller.apply_trans_live, 
            checkbox_width=18, checkbox_height=18
        )
        self.check_bin.pack(side="left")
        
        self.val_bin = ctk.CTkLabel(self.bin_header, text="127", font=ctk.CTkFont(size=10), text_color="#3d85c6")
        self.val_bin.pack(side="right")
        
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

        self.slider_bin = ctk.CTkSlider(
            self.frame_bin_main, from_=0, to=255, 
            command=self.on_bin_slider_change
        )
        self.slider_bin.set(127)
        self.slider_bin.pack(fill="x", padx=10, pady=(5, 10))
        
        # Painel secundário para parâmetros de binarização adaptativa
        self.frame_adaptive = ctk.CTkFrame(self.frame_bin_main, fg_color="transparent")
        
        fs_block = ctk.CTkFrame(self.frame_adaptive, fg_color="transparent")
        fs_block.pack(fill="x", pady=2)
        ctk.CTkLabel(fs_block, text="Block Size (Odd):", font=ctk.CTkFont(size=9), text_color="#aaa").pack(side="left")
        self.val_bin_block_size = ctk.CTkLabel(fs_block, text="11", font=ctk.CTkFont(size=9), text_color="#3d85c6")
        self.val_bin_block_size.pack(side="right")
        
        self.slider_bin_block_size = ctk.CTkSlider(
            self.frame_adaptive, from_=3, to=99, number_of_steps=48, 
            command=self.on_adaptive_param_change
        )
        self.slider_bin_block_size.set(11)
        self.slider_bin_block_size.pack(fill="x", padx=5, pady=(0, 5))
        
        fs_c = ctk.CTkFrame(self.frame_adaptive, fg_color="transparent")
        fs_c.pack(fill="x", pady=2)
        ctk.CTkLabel(fs_c, text="Constant C:", font=ctk.CTkFont(size=9), text_color="#aaa").pack(side="left")
        self.val_bin_c = ctk.CTkLabel(fs_c, text="2", font=ctk.CTkFont(size=9), text_color="#3d85c6")
        self.val_bin_c.pack(side="right")
        
        self.slider_bin_c = ctk.CTkSlider(
            self.frame_adaptive, from_=-20, to=20, 
            command=self.on_adaptive_param_change
        )
        self.slider_bin_c.set(2)
        self.slider_bin_c.pack(fill="x", padx=5, pady=(0, 5))
        
        # Botão de Commit global dos ajustes
        ctk.CTkButton(
            self, text="COMMIT ALL ADJUSTMENTS", command=self.app.controller.commit_changes, 
            fg_color="#3d85c6", hover_color="#2966a3", height=35, 
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=15, padx=10, fill="x")

    def create_slider_group(self, parent, label, start, end, val, callback):
        frame = ctk.CTkFrame(parent, fg_color="#333", corner_radius=8, border_width=1, border_color="#444")
        frame.pack(fill="x", pady=5, padx=5)
        
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(8, 0))
        
        ctk.CTkLabel(header, text=label.upper(), font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(side="left")
        
        val_label = ctk.CTkLabel(header, text=f"{val:+}" if val != 0 else str(val), font=ctk.CTkFont(size=10), text_color="#3d85c6")
        val_label.pack(side="right")
        
        slider = ctk.CTkSlider(frame, from_=start, to=end, command=lambda v: callback(v, val_label))
        slider.set(val)
        slider.pack(fill="x", padx=10, pady=(5, 12))
        
        return slider, val_label

    def on_adjust_slider_change(self, val, label_widget):
        label_widget.configure(text=f"{int(val):+}")
        self.app.controller.apply_trans_live()

    def on_bin_slider_change(self, val):
        self.val_bin.configure(text=str(int(val)))
        self.app.controller.apply_trans_live()

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
        self.app.controller.apply_trans_live()

    def on_adaptive_param_change(self, _=None):
        block_val = int(self.slider_bin_block_size.get())
        if block_val % 2 == 0:
            block_val += 1
        self.val_bin_block_size.configure(text=str(block_val))
        
        c_val = int(self.slider_bin_c.get())
        self.val_bin_c.configure(text=str(c_val))
        
        self.app.controller.apply_trans_live()

    # APIs públicas para recuperação do estado interno
    def get_brightness(self) -> float:
        return self.slider_bright.get()

    def get_contrast(self) -> float:
        return self.slider_contrast.get()

    def is_bin_enabled(self) -> bool:
        return self.bin_enabled.get()

    def get_bin_method(self) -> str:
        return self.bin_method.get()

    def get_bin_threshold(self) -> int:
        return int(self.slider_bin.get())

    def get_bin_block_size(self) -> int:
        block_val = int(self.slider_bin_block_size.get())
        if block_val % 2 == 0:
            block_val += 1
        return block_val

    def get_bin_c(self) -> float:
        return float(self.slider_bin_c.get())

    def reset_ui(self):
        self.slider_bright.set(0)
        self.val_bright.configure(text="0")
        self.slider_contrast.set(0)
        self.val_contrast.configure(text="0")
        
        self.bin_enabled.set(False)
        self.bin_method.set("Binary")
        self.opt_bin_method.set("Binary")
        
        self.slider_bin.set(127)
        self.val_bin.configure(text="127")
        
        self.slider_bin_block_size.set(11)
        self.val_bin_block_size.configure(text="11")
        
        self.slider_bin_c.set(2)
        self.val_bin_c.configure(text="2")
        
        self.slider_bin.configure(state="normal")
        self.frame_adaptive.pack_forget()
