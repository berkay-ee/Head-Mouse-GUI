import flet as ft

class CursorControlPage(ft.Container):
    def __init__(self, mouse_controller, current_theme=None):
        super().__init__()
        self.mouse_controller = mouse_controller
        self.expand = True
        self.padding = 30
        self.bgcolor = ft.Colors.TRANSPARENT

        # Tema Yedeği
        self.current_theme = current_theme if current_theme else {
            "bg": "#F8FAFC", "surface": "#FFFFFF", "primary": "#2563EB", 
            "text": "#0F172A", "text_secondary": "#64748B", "border": "#E2E8F0"
        }

        # Durumu Korunan Metin Bileşenleri (Tema değişse de değerleri sıfırlanmaz)
        self.text_sens_x = ft.Text("", weight=ft.FontWeight.BOLD)
        self.text_sens_y = ft.Text("", weight=ft.FontWeight.BOLD)
        self.text_deadzone = ft.Text("", weight=ft.FontWeight.BOLD)
        self.text_smoothing = ft.Text("", weight=ft.FontWeight.BOLD)
        
        # İlk Değerleri Yazdır
        self._update_text_values()

        # Arayüzü Çiz
        self.build_ui()

    def apply_theme(self, new_theme):
        """ Changes the current theme and rebuilds the UI to reflect the new theme. 
        (Main.py will call this when the user changes the theme) """
        self.current_theme = new_theme
        self.build_ui()
        try:
            self.update()
        except Exception:
            pass

    def _update_text_values(self):
        """ Updates the text components to reflect the current values from the mouse_controller. """
        self.text_sens_x.value = f"Horizontal Sensitivity (X): Current Value ({self.mouse_controller.sensitivity_x})"
        self.text_sens_y.value = f"Vertical Sensitivity (Y): Current Value ({self.mouse_controller.sensitivity_y})"
        self.text_deadzone.value = f"Dead Zone (Stability): Current Value ({self.mouse_controller.deadzone_yaw:.2f}°)"
        self.text_smoothing.value = f"Smoothing (Smoothness): Current Value ({self.mouse_controller.smoothing_factor:.2f})"

    # ==========================================
    # SENSITIVITY, DEADZONE, SMOOTHING SETTER Functions
    # ==========================================
    def set_sens_x(self, level):
        val = level * 10.0
        self.mouse_controller.sensitivity_x = val
        self.text_sens_x.value = f"Horizontal Sensitivity (X): Level {level} (Value: {val})"
        try:
            self.text_sens_x.update()
        except Exception:
            pass

    def set_sens_y(self, level):
        val = level * 10.0
        self.mouse_controller.sensitivity_y = val
        self.text_sens_y.value = f"Vertical Sensitivity (Y): Level {level} (Value: {val})"
        try:
            self.text_sens_y.update()
        except Exception:
            pass

    def set_deadzone(self, level):
        val = (level - 1) * 0.25 
        self.mouse_controller.deadzone_yaw = val
        self.mouse_controller.deadzone_pitch = val
        self.text_deadzone.value = f"Dead Zone (Stability): Level {level} (Value: {val:.2f}°)"
        try:
            self.text_deadzone.update()
        except Exception:
            pass
            
    def set_smoothing(self, level):
        val = (1/level) 
        self.mouse_controller.smoothing_factor = val
        self.text_smoothing.value = f"Smoothing (Smoothness %) : Level {level} (Value: {val:.2f})"
        try:
            self.text_smoothing.update()
        except Exception:
            pass

    # ==========================================
    # UI OLUŞTURMA FONKSİYONU
    # ==========================================
    def build_ui(self):
        theme = self.current_theme

        # 1. Adapt text colors to the current theme
        self.text_sens_x.color = theme["text"]
        self.text_sens_y.color = theme["text"]
        self.text_deadzone.color = theme["text"]
        self.text_smoothing.color = theme["text"]

        # 2. Common card border with Accent Line on the left
        card_border = ft.Border(
            top=ft.BorderSide(1, theme["border"]),
            right=ft.BorderSide(1, theme["border"]),
            bottom=ft.BorderSide(1, theme["border"]),
            left=ft.BorderSide(4, theme["primary"]) 
        )

        # 3. Dynamic Level Selector Button Factory
        def create_level_selector(action_func, current_level=9):
            buttons = []
            
            def handle_click(e):
                selected_level = e.control.data
                
                # Update visual state for all buttons in this row
                for btn in buttons:
                    if btn.data == selected_level:
                        # Active State Styling (Blue filled with blue border)
                        btn.bgcolor = theme["primary"]
                        btn.content.color = ft.Colors.WHITE
                        btn.border = ft.Border(
                            top=ft.BorderSide(2, theme["primary"]),
                            bottom=ft.BorderSide(2, theme["primary"]),
                            left=ft.BorderSide(2, theme["primary"]),
                            right=ft.BorderSide(2, theme["primary"])
                        )
                    else:
                        # Inactive State Styling (Transparent/Surface with grey border)
                        btn.bgcolor = theme["surface"]
                        btn.content.color = theme["text"]
                        btn.border = ft.Border(
                            top=ft.BorderSide(1, theme["border"]),
                            bottom=ft.BorderSide(1, theme["border"]),
                            left=ft.BorderSide(1, theme["border"]),
                            right=ft.BorderSide(1, theme["border"])
                        )
                    btn.update()
                    
                # Trigger the callback to update the backend math & labels
                action_func(selected_level)

            # Build the 20 buttons for the row
            for i in range(1, 21):
                is_selected = (i == current_level)
                
                btn = ft.Container(
                    content=ft.Text(str(i), color=ft.Colors.WHITE if is_selected else theme["text"], weight=ft.FontWeight.BOLD),
                    alignment=ft.Alignment(0, 0),  
                    width=40,
                    height=40,
                    border_radius=5,
                    ink=True,
                    data=i,
                    on_click=handle_click,
                    bgcolor=theme["primary"] if is_selected else theme["surface"],
                    border=ft.Border(
                        top=ft.BorderSide(2 if is_selected else 1, theme["primary"] if is_selected else theme["border"]),
                        bottom=ft.BorderSide(2 if is_selected else 1, theme["primary"] if is_selected else theme["border"]),
                        left=ft.BorderSide(2 if is_selected else 1, theme["primary"] if is_selected else theme["border"]),
                        right=ft.BorderSide(2 if is_selected else 1, theme["primary"] if is_selected else theme["border"])
                    )
                )
                buttons.append(btn)
                
            return ft.Row(buttons, wrap=True, spacing=5, run_spacing=5)


        # 4. Main Page Content Structure
        self.content = ft.Column([
            ft.Text("Cursor Control Settings", size=28, weight=ft.FontWeight.BOLD, color=theme["text"]),
            ft.Text("Select a level between 1 (Lowest) and 20 (Highest) to adjust sensitivity.", color=theme["text_secondary"]),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            
            # -----------------------------------------------------
            # CARD 1: Speed and Sensitivity 
            # -----------------------------------------------------
            ft.Container(
                content=ft.Column([
                    ft.Text("Speed and Sensitivity (px/mickey)", size=18, weight=ft.FontWeight.BOLD, color=theme["primary"]),
                    
                    self.text_sens_x,
                    create_level_selector(self.set_sens_x, current_level=9), 
                    
                    ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                    
                    self.text_sens_y,
                    create_level_selector(self.set_sens_y, current_level=6), 
                ]),
                padding=25, bgcolor=theme["surface"], border_radius=10,
                border=card_border,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK_12)
            ),
            
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            
            # -----------------------------------------------------
            # CARD 2: Stability and Filtering
            # -----------------------------------------------------
            ft.Container(
                content=ft.Column([
                    ft.Text("Filtering and Stability", size=18, weight=ft.FontWeight.BOLD, color=theme["primary"]),
                    
                    self.text_deadzone,
                    create_level_selector(self.set_deadzone, current_level=3), 
                    ft.Text("Prevents cursor tremor when looking straight ahead. (20 = Most sensitive)", size=12, color=theme["text_secondary"]),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    self.text_smoothing,
                    create_level_selector(self.set_smoothing, current_level=5), 
                    ft.Text("Smoothing Factor: 1-Instant response, rigid.", size=12, color=theme["text_secondary"]),
                ]),
                padding=20, bgcolor=theme["surface"], border_radius=10,
                border=card_border,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK_12)
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.START, scroll=ft.ScrollMode.AUTO)