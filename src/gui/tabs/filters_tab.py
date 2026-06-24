import customtkinter as ctk

class FiltersTab(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        """
        Aba de Filtros (Filtros Espaciais: Gaussian Blur, Median, Sobel, Laplacian).
        
        Parâmetros:
            master: Widget pai.
            app: Instância de ImageApp.
        """
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        # Seleção de Filtro
        choice_frame = ctk.CTkFrame(self, fg_color="#242424", corner_radius=8, border_width=1, border_color="#3a3a3a")
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
        
        self.lbl_choice = ctk.CTkLabel(
            choice_frame, text="Selecione um filtro para ajustar suas propriedades e aplicar na imagem.", 
            font=ctk.CTkFont(size=8, slant="italic"), text_color="#888", wraplength=220, justify="left"
        )
        self.lbl_choice.pack(anchor="w", fill="x", padx=10, pady=(0, 10))

        # Container dos frames dinâmicos de parâmetros
        self.filter_params_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_params_frame.pack(fill="x", pady=5)
        
        # 1. Painel Gaussiano
        self.frame_param_gaussian = ctk.CTkFrame(self.filter_params_frame, fg_color="#242424", corner_radius=8, border_width=1, border_color="#3a3a3a")
        ctk.CTkLabel(self.frame_param_gaussian, text="GAUSSIAN BLUR PARAMETERS", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(pady=(8, 2))
        
        fs_g_k = ctk.CTkFrame(self.frame_param_gaussian, fg_color="transparent")
        fs_g_k.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(fs_g_k, text="Kernel Size (Odd):", font=ctk.CTkFont(size=9), text_color="#aaa").pack(side="left")
        self.val_filter_gauss_k = ctk.CTkLabel(fs_g_k, text="5", font=ctk.CTkFont(size=9), text_color="#3d85c6")
        self.val_filter_gauss_k.pack(side="right")
        self.slider_filter_gauss_k = ctk.CTkSlider(self.frame_param_gaussian, from_=1, to=21, number_of_steps=10, command=self.on_filter_param_change, progress_color="#3d85c6", button_color="#3d85c6", button_hover_color="#2966a3")
        self.slider_filter_gauss_k.set(5)
        self.slider_filter_gauss_k.pack(fill="x", padx=10, pady=(0, 5))
        
        fs_g_s = ctk.CTkFrame(self.frame_param_gaussian, fg_color="transparent")
        fs_g_s.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(fs_g_s, text="Sigma (Std Dev):", font=ctk.CTkFont(size=9), text_color="#aaa").pack(side="left")
        self.val_filter_gauss_s = ctk.CTkLabel(fs_g_s, text="1.0", font=ctk.CTkFont(size=9), text_color="#3d85c6")
        self.val_filter_gauss_s.pack(side="right")
        self.slider_filter_gauss_s = ctk.CTkSlider(self.frame_param_gaussian, from_=0.1, to=10.0, command=self.on_filter_param_change, progress_color="#3d85c6", button_color="#3d85c6", button_hover_color="#2966a3")
        self.slider_filter_gauss_s.set(1.0)
        self.slider_filter_gauss_s.pack(fill="x", padx=10, pady=(0, 6))
        
        self.lbl_gauss = ctk.CTkLabel(self.frame_param_gaussian, text="Aplica uma suavização gaussiana. Ideal para redução de ruído genérico.", font=ctk.CTkFont(size=8, slant="italic"), text_color="#888", wraplength=220, justify="left")
        self.lbl_gauss.pack(anchor="w", fill="x", padx=10, pady=(0, 10))
        
        # 2. Painel Mediana
        self.frame_param_median = ctk.CTkFrame(self.filter_params_frame, fg_color="#242424", corner_radius=8, border_width=1, border_color="#3a3a3a")
        ctk.CTkLabel(self.frame_param_median, text="MEDIAN FILTER PARAMETERS", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(pady=(8, 2))
        
        fs_m_k = ctk.CTkFrame(self.frame_param_median, fg_color="transparent")
        fs_m_k.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(fs_m_k, text="Kernel Size (Odd):", font=ctk.CTkFont(size=9), text_color="#aaa").pack(side="left")
        self.val_filter_median_k = ctk.CTkLabel(fs_m_k, text="5", font=ctk.CTkFont(size=9), text_color="#3d85c6")
        self.val_filter_median_k.pack(side="right")
        self.slider_filter_median_k = ctk.CTkSlider(self.frame_param_median, from_=1, to=21, number_of_steps=10, command=self.on_filter_param_change, progress_color="#3d85c6", button_color="#3d85c6", button_hover_color="#2966a3")
        self.slider_filter_median_k.set(5)
        self.slider_filter_median_k.pack(fill="x", padx=10, pady=(0, 6))
        
        self.lbl_median = ctk.CTkLabel(self.frame_param_median, text="Filtro de mediana. Excelente para remoção de ruídos tipo sal e pimenta.", font=ctk.CTkFont(size=8, slant="italic"), text_color="#888", wraplength=220, justify="left")
        self.lbl_median.pack(anchor="w", fill="x", padx=10, pady=(0, 10))
        
        # 3. Painel Sobel
        self.frame_param_sobel = ctk.CTkFrame(self.filter_params_frame, fg_color="#242424", corner_radius=8, border_width=1, border_color="#3a3a3a")
        ctk.CTkLabel(self.frame_param_sobel, text="SOBEL EDGES PARAMETERS", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(pady=(8, 2))
        
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
        
        fs_s_k = ctk.CTkFrame(self.frame_param_sobel, fg_color="transparent")
        fs_s_k.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(fs_s_k, text="Kernel Size (Odd):", font=ctk.CTkFont(size=9), text_color="#aaa").pack(side="left")
        self.val_filter_sobel_k = ctk.CTkLabel(fs_s_k, text="3", font=ctk.CTkFont(size=9), text_color="#3d85c6")
        self.val_filter_sobel_k.pack(side="right")
        self.slider_filter_sobel_k = ctk.CTkSlider(self.frame_param_sobel, from_=1, to=7, number_of_steps=3, command=self.on_filter_param_change, progress_color="#3d85c6", button_color="#3d85c6", button_hover_color="#2966a3")
        self.slider_filter_sobel_k.set(3)
        self.slider_filter_sobel_k.pack(fill="x", padx=10, pady=(0, 6))
        
        self.lbl_sobel = ctk.CTkLabel(self.frame_param_sobel, text="Destaca gradientes e transições de intensidade. Útil para detecção de bordas orientadas.", font=ctk.CTkFont(size=8, slant="italic"), text_color="#888", wraplength=220, justify="left")
        self.lbl_sobel.pack(anchor="w", fill="x", padx=10, pady=(0, 10))
        
        # 4. Painel Laplacian
        self.frame_param_laplacian = ctk.CTkFrame(self.filter_params_frame, fg_color="#242424", corner_radius=8, border_width=1, border_color="#3a3a3a")
        ctk.CTkLabel(self.frame_param_laplacian, text="LAPLACIAN EDGES PARAMETERS", font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaa").pack(pady=(8, 2))
        
        fs_l_k = ctk.CTkFrame(self.frame_param_laplacian, fg_color="transparent")
        fs_l_k.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(fs_l_k, text="Kernel Size (Odd):", font=ctk.CTkFont(size=9), text_color="#aaa").pack(side="left")
        self.val_filter_laplacian_k = ctk.CTkLabel(fs_l_k, text="3", font=ctk.CTkFont(size=9), text_color="#3d85c6")
        self.val_filter_laplacian_k.pack(side="right")
        self.slider_filter_laplacian_k = ctk.CTkSlider(self.frame_param_laplacian, from_=1, to=7, number_of_steps=3, command=self.on_filter_param_change, progress_color="#3d85c6", button_color="#3d85c6", button_hover_color="#2966a3")
        self.slider_filter_laplacian_k.set(3)
        self.slider_filter_laplacian_k.pack(fill="x", padx=10, pady=(0, 6))
        
        self.lbl_laplacian = ctk.CTkLabel(self.frame_param_laplacian, text="Realça contornos usando a segunda derivada. Destaca todas as direções igualmente.", font=ctk.CTkFont(size=8, slant="italic"), text_color="#888", wraplength=220, justify="left")
        self.lbl_laplacian.pack(anchor="w", fill="x", padx=10, pady=(0, 10))

        # Painel de Ações
        self.frame_filter_action = ctk.CTkFrame(self, fg_color="#242424", corner_radius=8, border_width=1, border_color="#3a3a3a")
        self.frame_filter_action.pack(fill="x", pady=10, padx=5)
        
        self.filter_preview_enabled = ctk.BooleanVar(value=True)
        self.check_filter_preview = ctk.CTkCheckBox(
            self.frame_filter_action, text="LIVE PREVIEW", font=ctk.CTkFont(size=10, weight="bold"), 
            variable=self.filter_preview_enabled, command=self.app.controller.apply_filters_live, 
            checkbox_width=18, checkbox_height=18
        )
        self.check_filter_preview.pack(fill="x", padx=15, pady=(15, 5))
        
        self.btn_commit_filter = ctk.CTkButton(
            self.frame_filter_action, text="COMMIT FILTER", command=self.app.controller.commit_filter_action, 
            height=30, fg_color="#3d85c6", hover_color="#2966a3", font=ctk.CTkFont(size=10, weight="bold")
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
            
        self.app.controller.apply_filters_live()

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
        
        self.app.controller.apply_filters_live()

    def update_layout(self, width: int):
        """Atualiza a quebra de linha de todos os labels descritivos do painel de filtros."""
        w = width - 45
        if w < 50:
            w = 200
        self.lbl_choice.configure(wraplength=w)
        self.lbl_gauss.configure(wraplength=w)
        self.lbl_median.configure(wraplength=w)
        self.lbl_sobel.configure(wraplength=w)
        self.lbl_laplacian.configure(wraplength=w)

    # APIs públicas para recuperação do estado interno
    def get_filter_choice(self) -> str:
        return self.filter_choice.get()

    def is_preview_enabled(self) -> bool:
        return self.filter_preview_enabled.get()

    def get_gaussian_params(self) -> tuple[int, float]:
        gk = int(self.slider_filter_gauss_k.get())
        if gk % 2 == 0: gk += 1
        gs = self.slider_filter_gauss_s.get()
        return gk, gs

    def get_median_params(self) -> int:
        mk = int(self.slider_filter_median_k.get())
        if mk % 2 == 0: mk += 1
        return mk

    def get_sobel_params(self) -> tuple[str, int]:
        sk = int(self.slider_filter_sobel_k.get())
        if sk % 2 == 0: sk += 1
        mode_map = {"Horizontal": "horizontal", "Vertical": "vertical", "Combined": "both"}
        s_dir = mode_map.get(self.sobel_direction.get(), "both")
        return s_dir, sk

    def get_laplacian_params(self) -> int:
        lk = int(self.slider_filter_laplacian_k.get())
        if lk % 2 == 0: lk += 1
        return lk

    def reset_ui(self):
        self.filter_choice.set("None")
        self.filter_choice_menu.set("None")
        
        self.frame_param_gaussian.pack_forget()
        self.frame_param_median.pack_forget()
        self.frame_param_sobel.pack_forget()
        self.frame_param_laplacian.pack_forget()
        
        self.slider_filter_gauss_k.set(5)
        self.val_filter_gauss_k.configure(text="5")
        self.slider_filter_gauss_s.set(1.0)
        self.val_filter_gauss_s.configure(text="1.0")
        
        self.slider_filter_median_k.set(5)
        self.val_filter_median_k.configure(text="5")
        
        self.sobel_direction.set("Combined")
        self.opt_sobel_direction.set("Combined")
        self.slider_filter_sobel_k.set(3)
        self.val_filter_sobel_k.configure(text="3")
        
        self.slider_filter_laplacian_k.set(3)
        self.val_filter_laplacian_k.configure(text="3")
