import flet as ft

class MouseBindingsPage(ft.Container):
    def __init__(self, dwell_clicker):
        super().__init__()
        self.dwell_clicker = dwell_clicker
        self.expand = True
        self.padding = 30
        self.bgcolor = ft.Colors.TRANSPARENT

        # STATE
        self.active_click_method = "dwell"
        if self.dwell_clicker:
            self.dwell_clicker.enabled = True

        header = ft.Text("Mouse & Gesture Settings", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_87)

        # Active Mode Display
        self.mode_display = ft.Text("Current Action: Left Click", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
        
        mode_card = self.create_card(
            title="Action Cycler (Open Mouth)",
            icon=ft.Icons.SYNC,
            content=ft.Column([
                ft.Text("Opening your mouth cycles through Left Click, Right Click, Double Click, and Scroll Mode.", color=ft.Colors.BLACK_54),
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                self.mode_display
            ])
        )

        # Click Method Selector (Now includes "None")
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

        method_card = self.create_card(
            title="Click Execution Method",
            icon=ft.Icons.ADS_CLICK,
            content=ft.Column([
                ft.Text("Choose ONE method. The other will be disabled automatically.", color=ft.Colors.BLACK_54),
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                self.method_selector
            ])
        )

        # Dwell Settings
        initial_level = self.get_current_level()
        self.dwell_time_label = ft.Text(
            f"Dwell Time: Current Value ({self.dwell_clicker.dwell_time:.2f} Seconds)" if self.dwell_clicker else "Dwell Time: Current Value (1.50 Seconds)", 
            size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_87
        )

        self.level_buttons = []
        level_controls = []
        for lvl in range(1, 18):
            is_active = (lvl == initial_level)
            btn = ft.Button(
                content=ft.Text(str(lvl), text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.W_500, size=13),
                width=38, height=36,
                style=ft.ButtonStyle(padding=0, shape=ft.RoundedRectangleBorder(radius=8)),
                bgcolor=ft.Colors.ORANGE_50 if is_active else ft.Colors.WHITE,
                color=ft.Colors.ORANGE_900 if is_active else ft.Colors.BLACK_87,
                on_click=lambda e, l=lvl: self.set_dwell_level(l)
            )
            self.level_buttons.append((lvl, btn))
            level_controls.append(btn)

        levels_row = ft.Row(level_controls, spacing=5, scroll=ft.ScrollMode.AUTO)

        dwell_card = self.create_card(
            title="Dwell Click Speed",
            icon=ft.Icons.TIMER,
            content=ft.Column([
                self.dwell_time_label,
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                levels_row,
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                ft.Text("1 = Fastest (0.15 s) | 17 = Slowest (2.55 s)", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_800),
            ])
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
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icon, color=ft.Colors.BLUE_600), ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_87)]),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                content
            ]),
            padding=24, bgcolor=ft.Colors.WHITE, border_radius=12,
            border=ft.Border(
                top=ft.BorderSide(1, ft.Colors.BLACK_12), right=ft.BorderSide(1, ft.Colors.BLACK_12),
                bottom=ft.BorderSide(1, ft.Colors.BLACK_12), left=ft.BorderSide(1, ft.Colors.BLACK_12)
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
        
        # Blindly try to update visuals. If Flet complains it's not on screen yet, ignore it!
        try:
            self.mode_display.update()
            self.update() 
        except Exception:
            pass

    def get_current_level(self):
        if not self.dwell_clicker: return 10
        return max(1, min(17, int(round(self.dwell_clicker.dwell_time / 0.15))))

    def set_dwell_level(self, level):
        if self.dwell_clicker:
            self.dwell_clicker.dwell_time = level * 0.15
            self.dwell_time_label.value = f"Dwell Time: Current Value ({self.dwell_clicker.dwell_time:.2f} Seconds)"
            for lvl, btn in self.level_buttons:
                btn.bgcolor = ft.Colors.ORANGE_50 if lvl == level else ft.Colors.WHITE
                btn.color = ft.Colors.ORANGE_900 if lvl == level else ft.Colors.BLACK_87
                btn.update()
            self.dwell_time_label.update()