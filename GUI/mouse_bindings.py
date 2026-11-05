import flet as ft

class MouseBindingsPage(ft.Container):
    def __init__(self, dwell_clicker, current_theme=None):
        super().__init__()
        self.dwell_clicker = dwell_clicker
        self.expand = True
        self.padding = 30
        self.bgcolor = ft.Colors.TRANSPARENT

        # Eğer main.py'den tema gelmezse güvenlik yedeği
        self.current_theme = current_theme if current_theme else {
            "bg": "#F8FAFC", "surface": "#FFFFFF", "primary": "#2563EB", 
            "text": "#0F172A", "text_secondary": "#64748B", "border": "#E2E8F0"
        }

        # STATE
        self.active_click_method = "dwell"
        if self.dwell_clicker:
            self.dwell_clicker.enabled = True

        # UI ELEMENTS
        self.mode_display = ft.Text("Current Action: Left Click", size=22, weight=ft.FontWeight.BOLD)
        
        self.method_selector = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="dwell", label="Use Dwell Click (Hover to click)"),
                ft.Container(width=20),
                ft.Radio(value="blink", label="Use Eye Blink (Blink to click)"),
                ft.Container(width=20),
                ft.Radio(value="none", label="None (Disable Clicks)"),
            ], wrap=True),
            value="dwell",
            on_change=self.toggle_click_method
        )

        self.dwell_time_label = ft.Text("", size=14, weight=ft.FontWeight.BOLD)
        self.level_buttons = []

        # İlk arayüz çizimi
        self.build_ui()

    def apply_theme(self, new_theme):
        """ Changes the current theme and rebuilds the UI to reflect the new theme. """
        self.current_theme = new_theme
        self.build_ui()
        
        # if page is not None, update the page to reflect the new theme
        try:
            self.update()
        except Exception:
            pass

    def build_ui(self):
        """Arayüzü aktif temanın renkleriyle sıfırdan inşa eder."""
        theme = self.current_theme

        header = ft.Text("Mouse & Gesture Settings", size=28, weight=ft.FontWeight.BOLD, color=theme["text"])

        self.mode_display.color = theme["primary"]

        mode_card = self.create_card(
            title="Action Cycler (Open Mouth)",
            icon=ft.Icons.SYNC,
            content=ft.Column([
                ft.Text("Opening your mouth cycles through Left Click, Right Click, Double Click, and Scroll Mode.", color=theme["text_secondary"]),
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                self.mode_display
            ])
        )

        method_card = self.create_card(
            title="Click Execution Method",
            icon=ft.Icons.ADS_CLICK,
            content=ft.Column([
                ft.Text("Choose ONE method. The other will be disabled automatically.", color=theme["text_secondary"]),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.method_selector
            ])
        )

        # Dwell Settings Label Update
        if self.dwell_clicker:
            self.dwell_time_label.value = f"Dwell Time: Current Value ({self.dwell_clicker.dwell_time:.2f} Seconds)"
        else:
            self.dwell_time_label.value = "Dwell Time: Current Value (1.50 Seconds)"
        
        self.dwell_time_label.color = theme["text"]

        initial_level = self.get_current_level()
        self.level_buttons.clear()
        level_controls = []

        for lvl in range(1, 21):
            is_active = (lvl == initial_level)
            
            # If the button is active, use the primary color; otherwise, use the surface color for background.

            btn_bgcolor = theme["primary"] if is_active else theme["surface"]
            btn_color = ft.Colors.WHITE if is_active else theme["text"]

            btn = ft.Container(
                content=ft.Text(
                    str(lvl), 
                    size=13, 
                    weight=ft.FontWeight.W_500, 
                    color=ft.Colors.WHITE if is_active else theme["text"]
                ),
                alignment=ft.Alignment(0, 0),
                width=50, 
                height=50,
                border_radius=8,
                ink=True,  # Keeps the button click ripple effect
                data=lvl,
                on_click=lambda e, l=lvl: self.set_dwell_level(l),
                bgcolor=theme["primary"] if is_active else theme["surface"],
                border=ft.Border(
                    top=ft.BorderSide(2 if is_active else 1, theme["primary"] if is_active else theme["border"]),
                    bottom=ft.BorderSide(2 if is_active else 1, theme["primary"] if is_active else theme["border"]),
                    left=ft.BorderSide(2 if is_active else 1, theme["primary"] if is_active else theme["border"]),
                    right=ft.BorderSide(2 if is_active else 1, theme["primary"] if is_active else theme["border"])
                )
            )
            self.level_buttons.append((lvl, btn))
            level_controls.append(btn)

        levels_row = ft.Row(level_controls, spacing=5, run_spacing=10, wrap=True)

        dwell_card = self.create_card(
            title="Dwell Click Speed (Seconds)",
            icon=ft.Icons.TIMER,
            content=ft.Container(
                content=ft.Column([
                    self.dwell_time_label,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    levels_row,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Text("1 = Fastest (0.15 s) | 20 = Slowest (3.00 s)", size=12, weight=ft.FontWeight.BOLD, color=theme["primary"]),
                ]),
                padding=25, bgcolor=theme["surface"], border_radius=10,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK_12)

            )
        )

        

        self.content = ft.Column([
            header,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            mode_card,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            method_card,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            dwell_card
        ], horizontal_alignment=ft.CrossAxisAlignment.START, scroll=ft.ScrollMode.AUTO)

    def create_card(self, title, icon, content):
        theme = self.current_theme
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icon, color=theme["primary"]), ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=theme["text"])]),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                content
            ]),
            padding=24, bgcolor=theme["surface"], border_radius=12,
            border=ft.Border(
                top=ft.BorderSide(1, theme["border"]), right=ft.BorderSide(1, theme["border"]),
                bottom=ft.BorderSide(1, theme["border"]), left=ft.BorderSide(1, theme["border"])
            ),
            shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.BLACK_12)
        )

    def toggle_click_method(self, e):
        self.active_click_method = self.method_selector.value
        if self.dwell_clicker:
            self.dwell_clicker.enabled = (self.active_click_method == "dwell")
        print(f"[Settings] Click Method changed to: {self.active_click_method}")

    def update_active_mode_text(self, mode_name):
        """Safely updates the text display to exactly match the active mode."""
        self.mode_display.value = f"Current Action: {mode_name}"
        try:
            self.mode_display.update()
            self.update() 
        except Exception:
            pass

    def get_current_level(self):
        if not self.dwell_clicker: return 10
        return max(1, min(20, int(round(self.dwell_clicker.dwell_time / 0.15))))

    def set_dwell_level(self, level):
        theme = self.current_theme
        if self.dwell_clicker:
            self.dwell_clicker.dwell_time = level * 0.15
            self.dwell_time_label.value = f"Dwell Time: Current Value ({self.dwell_clicker.dwell_time:.2f} Seconds)"
            
            # Tıklanan butonun rengini temanın ana rengine dönüştür
            for lvl, btn in self.level_buttons:
                btn.bgcolor = theme["primary"] if lvl == level else theme["surface"]
                btn.color = ft.Colors.WHITE if lvl == level else theme["text"]
                btn.update()
                
            self.dwell_time_label.update()