import customtkinter as ctk

class MenuBar(ctk.CTkFrame):
    def __init__(self, master, app):
        """
        Inicializa a barra de menus superior.
        
        Parâmetros:
            master: Widget pai onde a barra de menus será inserida.
            app: Instância de ImageApp que contém as funções de callback.
        """
        super().__init__(master, height=35, corner_radius=0, fg_color="#2b2b2b", border_width=1, border_color="#1a1a1a")
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        menus = [
            ("File", ["File", "Open...", "Save", "Exit"], self.app.controller.handle_file_menu),
            ("Edit", ["Edit", "Undo", "Redo", "Reset Image"], self.app.controller.handle_edit_menu),
            ("Image", ["Image", "Grayscale", "Invert", "Equalize"], self.app.controller.handle_image_menu),
            ("Filter", ["Filter", "Gaussian Blur", "Median Filter", "Sobel Edges", "Laplacian"], self.app.controller.handle_filter_menu),
            ("View", ["View", "Zoom In", "Zoom Out", "Fit Screen"], self.app.controller.handle_view_menu),
            ("Window", ["Window", "Toggle Properties"], self.app.controller.handle_window_menu)
        ]

        def make_menu_callback(menu_widget, category_label, original_callback):
            return lambda choice: [original_callback(choice), menu_widget.set(category_label)]

        for label, vals, cmd in menus:
            m = ctk.CTkOptionMenu(
                self, 
                values=vals, 
                width=80, 
                height=25, 
                fg_color="#2b2b2b", 
                button_color="#2b2b2b", 
                button_hover_color="#3d3d3d", 
                dynamic_resizing=False
            )
            m.configure(command=make_menu_callback(m, label, cmd))
            m.set(label)
            m.pack(side="left", padx=2)
