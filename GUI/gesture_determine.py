import flet as ft

class GestureDeterminePage(ft.Container):
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

        # UI Constants
        self.max_angle = 18.0 
        self.bar_width = 400

        # ==========================================
        # DURUMU (STATE) KORUNAN BİLEŞENLER
        # ==========================================
        # Pitch (Up/Down) State
        self.pitch_threshold_val = 5.0
        if self.mouse_controller and hasattr(self.mouse_controller, 'scroll_threshold'):
            self.pitch_threshold_val = self.mouse_controller.scroll_threshold

        self.pitch_text = ft.Text(f"Current Pitch: 0.0°", size=16, weight=ft.FontWeight.BOLD)
        self.pitch_status = ft.Text("IDLE", weight=ft.FontWeight.BOLD)
        self.pitch_val_text = ft.Text(f"Pitch Threshold: Current Value ({self.pitch_threshold_val:.1f}°)", size=14, weight=ft.FontWeight.BOLD)
        
        self.pitch_dot = ft.Container(width=16, height=16, border_radius=8, left=self.bar_width/2 - 8, top=2)
        self.pitch_left_thresh = ft.Container(width=2, height=20, bgcolor=ft.Colors.RED, left=self._calc_pos(-self.pitch_threshold_val), top=0)
        self.pitch_right_thresh = ft.Container(width=2, height=20, bgcolor=ft.Colors.RED, left=self._calc_pos(self.pitch_threshold_val), top=0)
        self.pitch_center = ft.Container(width=2, height=20, left=self.bar_width/2 - 1, top=0)
        self.pitch_bar_bg = ft.Container(width=self.bar_width, height=20, border_radius=10)
        
        self.pitch_bar = ft.Stack([
            self.pitch_bar_bg, self.pitch_center, self.pitch_left_thresh, self.pitch_right_thresh, self.pitch_dot
        ], width=self.bar_width, height=20)

        # Yaw (Left/Right) State
        self.yaw_threshold_val = 5.0
        self.yaw_text = ft.Text(f"Current Yaw: 0.0°", size=16, weight=ft.FontWeight.BOLD)
        self.yaw_status = ft.Text("IDLE", weight=ft.FontWeight.BOLD)
        self.yaw_val_text = ft.Text(f"Yaw Threshold: Current Value ({self.yaw_threshold_val:.1f}°)", size=14, weight=ft.FontWeight.BOLD)
        
        self.yaw_dot = ft.Container(width=16, height=16, border_radius=8, left=self.bar_width/2 - 8, top=2)
        self.yaw_left_thresh = ft.Container(width=2, height=20, bgcolor=ft.Colors.RED, left=self._calc_pos(-self.yaw_threshold_val), top=0)
        self.yaw_right_thresh = ft.Container(width=2, height=20, bgcolor=ft.Colors.RED, left=self._calc_pos(self.yaw_threshold_val), top=0)
        self.yaw_center = ft.Container(width=2, height=20, left=self.bar_width/2 - 1, top=0)
        self.yaw_bar_bg = ft.Container(width=self.bar_width, height=20, border_radius=10)

        self.yaw_bar = ft.Stack([
            self.yaw_bar_bg, self.yaw_center, self.yaw_left_thresh, self.yaw_right_thresh, self.yaw_dot
        ], width=self.bar_width, height=20)

        self.pitch_buttons = []
        self.yaw_buttons = []

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

    def build_ui(self):
        """Arayüzü aktif temanın renkleriyle sıfırdan inşa eder."""
        theme = self.current_theme
        
        # Grafik renklerini güncelle
        self.pitch_text.color = theme["text"]
        self.pitch_val_text.color = theme["text"]
        self.pitch_status.color = theme["text_secondary"]
        self.pitch_dot.bgcolor = theme["primary"]
        self.pitch_bar_bg.bgcolor = theme["border"]
        self.pitch_center.bgcolor = theme["text_secondary"]

        self.yaw_text.color = theme["text"]
        self.yaw_val_text.color = theme["text"]
        self.yaw_status.color = theme["text_secondary"]
        self.yaw_dot.bgcolor = theme["primary"]
        self.yaw_bar_bg.bgcolor = theme["border"]
        self.yaw_center.bgcolor = theme["text_secondary"]

        # Pitch Seviye Butonları
        self.pitch_buttons.clear()
        pitch_controls = []
        initial_pitch_level = int(round(self.pitch_threshold_val))
        for lvl in range(1, 18):
            is_active = (lvl == initial_pitch_level)
            btn = ft.Button(
                str(lvl), width=38, height=36,
                style=ft.ButtonStyle(padding=0, shape=ft.RoundedRectangleBorder(radius=8)),
                bgcolor=theme["primary"] if is_active else theme["bg"],
                color=ft.Colors.WHITE if is_active else theme["text"],
                on_click=lambda e, l=lvl: self.set_pitch(l)
            )
            self.pitch_buttons.append((lvl, btn))
            pitch_controls.append(btn)
        pitch_row = ft.Row(pitch_controls, spacing=5, scroll=ft.ScrollMode.AUTO)

        # Yaw Seviye Butonları
        self.yaw_buttons.clear()
        yaw_controls = []
        initial_yaw_level = int(round(self.yaw_threshold_val))
        for lvl in range(1, 18):
            is_active = (lvl == initial_yaw_level)
            btn = ft.Button(
                str(lvl), width=38, height=36,
                style=ft.ButtonStyle(padding=0, shape=ft.RoundedRectangleBorder(radius=8)),
                bgcolor=theme["primary"] if is_active else theme["bg"],
                color=ft.Colors.WHITE if is_active else theme["text"],
                on_click=lambda e, l=lvl: self.set_yaw(l)
            )
            self.yaw_buttons.append((lvl, btn))
            yaw_controls.append(btn)
        yaw_row = ft.Row(yaw_controls, spacing=5, scroll=ft.ScrollMode.AUTO)

        # Sayfa Düzeni
        self.content = ft.Column([
            ft.Text("Head Movement Thresholds", size=28, weight=ft.FontWeight.BOLD, color=theme["text"]),
            ft.Text("Select a threshold value (1-17). When the blue dot (your head) passes the red line, the event triggers.", color=theme["text_secondary"]),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            
            self.create_card("Pitch / Vertical (Used for Scrolling Up & Down)", ft.Icons.SWAP_VERT, [
                ft.Row([self.pitch_text, self.pitch_status], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=400),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.pitch_bar,
                ft.Row([ft.Text("Down", size=12, color=theme["text_secondary"]), ft.Text("Center", size=12, color=theme["text_secondary"]), ft.Text("Up", size=12, color=theme["text_secondary"])], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=400),
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                self.pitch_val_text,
                pitch_row
            ]),
            
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),

            self.create_card("Yaw / Horizontal (Used for Left & Right)", ft.Icons.SWAP_HORIZ, [
                ft.Row([self.yaw_text, self.yaw_status], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=400),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.yaw_bar,
                ft.Row([ft.Text("Left", size=12, color=theme["text_secondary"]), ft.Text("Center", size=12, color=theme["text_secondary"]), ft.Text("Right", size=12, color=theme["text_secondary"])], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=400),
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                self.yaw_val_text,
                yaw_row
            ])
        ], scroll=ft.ScrollMode.AUTO)


    # ==========================================
    # HELPER METHODS
    # ==========================================
    def create_card(self, title, icon, controls):
        theme = self.current_theme
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icon, color=theme["primary"]), ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=theme["text"])]),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                *controls
            ]),
            padding=24, bgcolor=theme["surface"], border_radius=12,
            border=ft.Border(
                top=ft.BorderSide(1, theme["border"]), right=ft.BorderSide(1, theme["border"]), 
                bottom=ft.BorderSide(1, theme["border"]), left=ft.BorderSide(1, theme["border"])
            ),
            shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.BLACK_12)
        )

    def _calc_pos(self, angle):
        clamped_angle = max(-self.max_angle, min(self.max_angle, angle))
        return (self.bar_width / 2) + (clamped_angle * (self.bar_width / (self.max_angle * 2)))

    # --- BUTTON LOGIC FOR PITCH ---
    def set_pitch(self, level):
        theme = self.current_theme
        self.pitch_threshold_val = float(level)
        if self.mouse_controller:
            self.mouse_controller.scroll_threshold = self.pitch_threshold_val
            
        self.pitch_val_text.value = f"Pitch Threshold: Current Value ({self.pitch_threshold_val:.1f}°)"
        self.pitch_left_thresh.left = self._calc_pos(-self.pitch_threshold_val)
        self.pitch_right_thresh.left = self._calc_pos(self.pitch_threshold_val)

        for lvl, btn in self.pitch_buttons:
            is_active = (lvl == level)
            btn.bgcolor = theme["primary"] if is_active else theme["bg"]
            btn.color = ft.Colors.WHITE if is_active else theme["text"]
            try: btn.update()
            except: pass

        try:
            self.pitch_val_text.update()
            self.pitch_bar.update()
        except: pass

    # --- BUTTON LOGIC FOR YAW ---
    def set_yaw(self, level):
        theme = self.current_theme
        self.yaw_threshold_val = float(level)
        
        self.yaw_val_text.value = f"Yaw Threshold: Current Value ({self.yaw_threshold_val:.1f}°)"
        self.yaw_left_thresh.left = self._calc_pos(-self.yaw_threshold_val)
        self.yaw_right_thresh.left = self._calc_pos(self.yaw_threshold_val)

        for lvl, btn in self.yaw_buttons:
            is_active = (lvl == level)
            btn.bgcolor = theme["primary"] if is_active else theme["bg"]
            btn.color = ft.Colors.WHITE if is_active else theme["text"]
            try: btn.update()
            except: pass

        try:
            self.yaw_val_text.update()
            self.yaw_bar.update()
        except: pass

    # --- CANLI VERİ (LIVE DATA) ---
    def update_live_data(self, pitch, yaw):
        if not self.page: return 

        display_pitch = pitch
        if self.mouse_controller and self.mouse_controller.scroll_baseline_pitch is not None:
            display_pitch = pitch - self.mouse_controller.scroll_baseline_pitch

        self.pitch_dot.left = self._calc_pos(display_pitch) - 8 
        self.yaw_dot.left = self._calc_pos(yaw) - 8

        self.pitch_text.value = f"Current Pitch: {display_pitch:.1f}°"
        self.yaw_text.value = f"Current Yaw: {yaw:.1f}°"

        theme = self.current_theme

        # Pitch Status Update
        if display_pitch > self.pitch_threshold_val:
            self.pitch_status.value, self.pitch_status.color = "EXECUTING UP!", ft.Colors.GREEN
        elif display_pitch < -self.pitch_threshold_val:
            self.pitch_status.value, self.pitch_status.color = "EXECUTING DOWN!", ft.Colors.GREEN
        else:
            self.pitch_status.value, self.pitch_status.color = "IDLE", theme["text_secondary"]

        # Yaw Status Update
        if yaw > self.yaw_threshold_val:
            self.yaw_status.value, self.yaw_status.color = "EXECUTING RIGHT!", ft.Colors.GREEN
        elif yaw < -self.yaw_threshold_val:
            self.yaw_status.value, self.yaw_status.color = "EXECUTING LEFT!", ft.Colors.GREEN
        else:
            self.yaw_status.value, self.yaw_status.color = "IDLE", theme["text_secondary"]

        try:
            self.pitch_text.update()
            self.pitch_status.update()
            self.pitch_bar.update()
            self.yaw_text.update()
            self.yaw_status.update()
            self.yaw_bar.update()
        except Exception:
            pass