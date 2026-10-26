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
        """Tema değiştiğinde main.py tarafından tetiklenir."""
        self.current_theme = new_theme
        self.build_ui()
        try:
            self.update()
        except Exception:
            pass

    def _update_text_values(self):
        """Değer metinlerini güncel fare kontrolcüsü verileriyle doldurur."""
        self.text_sens_x.value = f"Horizontal Sensitivity (X): Current Value ({self.mouse_controller.sensitivity_x})"
        self.text_sens_y.value = f"Vertical Sensitivity (Y): Current Value ({self.mouse_controller.sensitivity_y})"
        self.text_deadzone.value = f"Dead Zone (Stability): Current Value ({self.mouse_controller.deadzone_yaw:.2f}°)"
        self.text_smoothing.value = f"Smoothing (Smoothness): Current Value ({self.mouse_controller.smoothing_factor:.2f})"

    # ==========================================
    # DEĞER GÜNCELLEME FONKSİYONLARI
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
        val = level * 0.05
        self.mouse_controller.smoothing_factor = val
        self.text_smoothing.value = f"Smoothing (Smoothness): Level {level} (Value: {val:.2f})"
        try:
            self.text_smoothing.update()
        except Exception:
            pass

    # ==========================================
    # ARAYÜZ İNŞA EDİCİ
    # ==========================================
    def build_ui(self):
        theme = self.current_theme

        # Metin renklerini temaya uyarla
        self.text_sens_x.color = theme["text"]
        self.text_sens_y.color = theme["text"]
        self.text_deadzone.color = theme["text"]
        self.text_smoothing.color = theme["text"]

        def create_level_buttons(action_func):
            buttons = []
            for i in range(1, 21):
                buttons.append(
                    ft.Button(
                        str(i), 
                        width=50,  
                        height=50, 
                        style=ft.ButtonStyle(
                            padding=0, 
                            shape=ft.RoundedRectangleBorder(radius=6),
                            bgcolor=theme["bg"], # Buton arka planı
                            color=theme["text"]  # Buton yazı rengi
                        ),
                        on_click=lambda e, level=i: action_func(level)
                    )
                )
            return ft.Row(buttons, wrap=True, spacing=5, run_spacing=5)

        # Kartlar için ortak kenarlık (Sadece solu kalın - Accent Line)
        card_border = ft.Border(
            top=ft.BorderSide(1, theme["border"]),
            right=ft.BorderSide(1, theme["border"]),
            bottom=ft.BorderSide(1, theme["border"]),
            left=ft.BorderSide(4, theme["primary"]) 
        )

        self.content = ft.Column([
            ft.Text("Cursor Control Settings", size=28, weight=ft.FontWeight.BOLD, color=theme["text"]),
            ft.Text("Select a level between 1 (Lowest) and 20 (Highest) to adjust sensitivity.", color=theme["text_secondary"]),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            
            # Speed and Sensitivity 
            ft.Container(
                content=ft.Column([
                    ft.Text("Speed and Sensitivity", size=18, weight=ft.FontWeight.BOLD, color=theme["primary"]),
                    self.text_sens_x,
                    create_level_buttons(self.set_sens_x), 
                    
                    ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                    
                    self.text_sens_y,
                    create_level_buttons(self.set_sens_y), 
                ]),
                padding=25, bgcolor=theme["surface"], border_radius=10,
                border=card_border,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK_12)
            ),
            
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            
            # stability and filtering
            ft.Container(
                content=ft.Column([
                    ft.Text("Filtering and Stability", size=18, weight=ft.FontWeight.BOLD, color=theme["primary"]),
                    self.text_deadzone,
                    create_level_buttons(self.set_deadzone), 
                    ft.Text("Prevents cursor tremor when looking straight ahead. (20 = Most sensitive)", size=12, color=theme["text_secondary"]),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    self.text_smoothing,
                    create_level_buttons(self.set_smoothing), 
                    ft.Text("Smoothing Factor: 1-Instant response, rigid.", size=12, color=theme["text_secondary"]),
                ]),
                padding=20, bgcolor=theme["surface"], border_radius=10,
                border=card_border,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK_12)
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.START, scroll=ft.ScrollMode.AUTO)