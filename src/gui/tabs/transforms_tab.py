import customtkinter as ctk

class TransformsTab(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        """
        Aba de Transformações Geométricas (Rotação, Escala e Redimensionamento de Pixels).
        
        Parâmetros:
            master: Widget pai.
            app: Instância de ImageApp.
        """
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        # --- SEÇÃO DE ROTAÇÃO ---
        rot_frame = ctk.CTkFrame(self, fg_color="#333", corner_radius=8, border_width=1, border_color="#444")
        rot_frame.pack(fill="x", pady=5, padx=5)
        
        rot_header = ctk.CTkFrame(rot_frame, fg_color="transparent")
        rot_header.pack(fill="x", padx=10, pady=(8, 0))
        ctk.CTkLabel(rot_header, text="ROTATION", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(side="left")
        self.val_rotate = ctk.CTkLabel(rot_header, text="0°", font=ctk.CTkFont(size=10), text_color="#3d85c6")
        self.val_rotate.pack(side="right")
        
        self.slider_rotate = ctk.CTkSlider(rot_frame, from_=-180, to=180, command=self.on_rotate_slider_change)
        self.slider_rotate.set(0)
        self.slider_rotate.pack(fill="x", padx=10, pady=(5, 5))
        
        self.rotate_keep_bounds = ctk.BooleanVar(value=True)
        self.check_keep_bounds = ctk.CTkCheckBox(
            rot_frame, text="Adjust Canvas to Fit", font=ctk.CTkFont(size=9), 
            variable=self.rotate_keep_bounds, command=self.app.controller.apply_rotate_live,
            checkbox_width=16, checkbox_height=16
        )
        self.check_keep_bounds.pack(anchor="w", padx=10, pady=(0, 10))
        
        quick_btn_frame = ctk.CTkFrame(rot_frame, fg_color="transparent")
        quick_btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(quick_btn_frame, text="-90°", width=50, height=24, command=lambda: self.app.controller.quick_rotate(-90), font=ctk.CTkFont(size=9)).pack(side="left", expand=True, padx=2)
        ctk.CTkButton(quick_btn_frame, text="90°", width=50, height=24, command=lambda: self.app.controller.quick_rotate(90), font=ctk.CTkFont(size=9)).pack(side="left", expand=True, padx=2)
        ctk.CTkButton(quick_btn_frame, text="180°", width=50, height=24, command=lambda: self.app.controller.quick_rotate(180), font=ctk.CTkFont(size=9)).pack(side="left", expand=True, padx=2)
        
        ctk.CTkButton(rot_frame, text="COMMIT ROTATION", command=self.app.controller.commit_rotation, height=26, fg_color="#444", font=ctk.CTkFont(size=10, weight="bold")).pack(fill="x", padx=10, pady=(0, 10))
        
        # --- SEÇÃO DE ESCALA ---
        scale_frame = ctk.CTkFrame(self, fg_color="#333", corner_radius=8, border_width=1, border_color="#444")
        scale_frame.pack(fill="x", pady=5, padx=5)
        
        scale_header = ctk.CTkFrame(scale_frame, fg_color="transparent")
        scale_header.pack(fill="x", padx=10, pady=(8, 0))
        ctk.CTkLabel(scale_header, text="SCALE", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(side="left")
        self.val_scale = ctk.CTkLabel(scale_header, text="1.00x", font=ctk.CTkFont(size=10), text_color="#3d85c6")
        self.val_scale.pack(side="right")
        
        self.slider_scale = ctk.CTkSlider(scale_frame, from_=0.1, to=3.0, command=self.on_scale_slider_change)
        self.slider_scale.set(1.0)
        self.slider_scale.pack(fill="x", padx=10, pady=(5, 10))
        
        ctk.CTkButton(scale_frame, text="COMMIT SCALE", command=self.app.controller.commit_scale, height=26, fg_color="#444", font=ctk.CTkFont(size=10, weight="bold")).pack(fill="x", padx=10, pady=(0, 10))
        
        # --- SEÇÃO DE REDIMENSIONAMENTO ---
        resize_frame = ctk.CTkFrame(self, fg_color="#333", corner_radius=8, border_width=1, border_color="#444")
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
            resize_frame, text="Constrain Proportions", font=ctk.CTkFont(size=9), 
            variable=self.lock_aspect_ratio, checkbox_width=16, checkbox_height=16
        )
        self.check_lock_aspect.pack(anchor="w", padx=10, pady=(5, 10))
        
        ctk.CTkButton(
            resize_frame, text="APPLY RESIZE", command=self.app.controller.commit_resize, 
            height=26, fg_color="#3d85c6", hover_color="#2966a3", 
            font=ctk.CTkFont(size=10, weight="bold")
        ).pack(fill="x", padx=10, pady=(0, 10))

    def on_rotate_slider_change(self, val):
        self.val_rotate.configure(text=f"{int(val)}°")
        self.app.controller.apply_rotate_live()

    def on_scale_slider_change(self, val):
        self.val_scale.configure(text=f"{val:.2f}x")
        self.app.controller.apply_scale_live()

    def on_width_changed(self, event=None):
        if not self.lock_aspect_ratio.get() or self.app.image_service.current_image is None:
            return
        try:
            val = self.entry_width.get()
            if not val:
                return
            w = int(val)
            h_orig, w_orig = self.app.image_service.current_image.shape[:2]
            aspect = h_orig / w_orig
            new_h = int(w * aspect)
            
            self.entry_height.delete(0, "end")
            self.entry_height.insert(0, str(new_h))
        except ValueError:
            pass

    def on_height_changed(self, event=None):
        if not self.lock_aspect_ratio.get() or self.app.image_service.current_image is None:
            return
        try:
            val = self.entry_height.get()
            if not val:
                return
            h = int(val)
            h_orig, w_orig = self.app.image_service.current_image.shape[:2]
            aspect = w_orig / h_orig
            new_w = int(h * aspect)
            
            self.entry_width.delete(0, "end")
            self.entry_width.insert(0, str(new_w))
        except ValueError:
            pass

    # APIs públicas para recuperação do estado interno
    def get_rotation_angle(self) -> float:
        return self.slider_rotate.get()

    def get_keep_bounds(self) -> bool:
        return self.rotate_keep_bounds.get()

    def get_scale(self) -> float:
        return self.slider_scale.get()

    def get_resize_dimensions(self) -> tuple[int, int]:
        w = int(self.entry_width.get())
        h = int(self.entry_height.get())
        return w, h

    def is_aspect_locked(self) -> bool:
        return self.lock_aspect_ratio.get()

    def reset_ui(self, current_image_shape: tuple[int, int] | None):
        self.slider_rotate.set(0)
        self.val_rotate.configure(text="0°")
        self.slider_scale.set(1.0)
        self.val_scale.configure(text="1.00x")
        self.rotate_keep_bounds.set(True)
        self.lock_aspect_ratio.set(True)
        
        self.entry_width.delete(0, "end")
        self.entry_height.delete(0, "end")
        
        if current_image_shape is not None:
            h, w = current_image_shape
            self.entry_width.insert(0, str(w))
            self.entry_height.insert(0, str(h))

    def update_dimensions(self, w: int, h: int):
        self.entry_width.delete(0, "end")
        self.entry_width.insert(0, str(w))
        self.entry_height.delete(0, "end")
        self.entry_height.insert(0, str(h))
