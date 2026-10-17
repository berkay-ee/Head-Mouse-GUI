import flet as ft

class GestureDeterminePage(ft.Container):
    def __init__(self, mouse_controller):
        super().__init__()
        self.mouse_controller = mouse_controller
        self.expand = True
        self.padding = 30
        self.bgcolor = ft.Colors.TRANSPARENT

        # UI Constants
        self.max_angle = 18.0 # Increased to 18 so the 17 degree threshold fits on the bar
        self.bar_width = 400

        # ==========================================
        # PITCH (UP / DOWN) SECTION
        # ==========================================
        self.pitch_threshold_val = 5.0
        if self.mouse_controller and hasattr(self.mouse_controller, 'scroll_threshold'):
            self.pitch_threshold_val = self.mouse_controller.scroll_threshold

        self.pitch_text = ft.Text(f"Current Pitch: 0.0°", size=16, weight=ft.FontWeight.BOLD)
        self.pitch_status = ft.Text("IDLE", color=ft.Colors.GREY, weight=ft.FontWeight.BOLD)
        self.pitch_val_text = ft.Text(f"Pitch Threshold: Current Value ({self.pitch_threshold_val:.1f}°)", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_87)
        
        # Build 1-17 Buttons for Pitch
        self.pitch_buttons = []
        pitch_controls = []
        initial_pitch_level = int(round(self.pitch_threshold_val))
        
        for lvl in range(1, 18):
            is_active = (lvl == initial_pitch_level)
            btn = ft.Button(
                content=ft.Text(str(lvl), text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.W_500, size=13),
                width=38,
                height=36,
                style=ft.ButtonStyle(padding=0, shape=ft.RoundedRectangleBorder(radius=8)),
                bgcolor=ft.Colors.BLUE_50 if is_active else ft.Colors.BLUE_GREY_50,
                color=ft.Colors.BLUE_900 if is_active else ft.Colors.BLACK_87,
                on_click=lambda e, l=lvl: self.set_pitch(l)
            )
            self.pitch_buttons.append((lvl, btn))
            pitch_controls.append(btn)

        self.pitch_row = ft.Row(pitch_controls, spacing=5, scroll=ft.ScrollMode.AUTO)

        # Graphical Bar for Pitch
        self.pitch_dot = ft.Container(width=16, height=16, border_radius=8, bgcolor=ft.Colors.BLUE, left=self.bar_width/2 - 8, top=2)
        self.pitch_left_thresh = ft.Container(width=2, height=20, bgcolor=ft.Colors.RED, left=self._calc_pos(-self.pitch_threshold_val), top=0)
        self.pitch_right_thresh = ft.Container(width=2, height=20, bgcolor=ft.Colors.RED, left=self._calc_pos(self.pitch_threshold_val), top=0)
        self.pitch_center = ft.Container(width=2, height=20, bgcolor=ft.Colors.BLACK_54, left=self.bar_width/2 - 1, top=0)
        
        self.pitch_bar = ft.Stack([
            ft.Container(width=self.bar_width, height=20, bgcolor=ft.Colors.GREY_200, border_radius=10),
            self.pitch_center,
            self.pitch_left_thresh,
            self.pitch_right_thresh,
            self.pitch_dot
        ], width=self.bar_width, height=20)

        # ==========================================
        # YAW (LEFT / RIGHT) SECTION
        # ==========================================
        self.yaw_threshold_val = 5.0
        self.yaw_text = ft.Text(f"Current Yaw: 0.0°", size=16, weight=ft.FontWeight.BOLD)
        self.yaw_status = ft.Text("IDLE", color=ft.Colors.GREY, weight=ft.FontWeight.BOLD)
        self.yaw_val_text = ft.Text(f"Yaw Threshold: Current Value ({self.yaw_threshold_val:.1f}°)", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_87)
        
        # Build 1-17 Buttons for Yaw
        self.yaw_buttons = []
        yaw_controls = []
        initial_yaw_level = int(round(self.yaw_threshold_val))

        for lvl in range(1, 18):
            is_active = (lvl == initial_yaw_level)
            btn = ft.Button(
                content=ft.Text(str(lvl), text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.W_500, size=13),
                width=38,
                height=36,
                style=ft.ButtonStyle(padding=0, shape=ft.RoundedRectangleBorder(radius=8)),
                bgcolor=ft.Colors.BLUE_50 if is_active else ft.Colors.BLUE_GREY_50,
                color=ft.Colors.BLUE_900 if is_active else ft.Colors.BLACK_87,
                on_click=lambda e, l=lvl: self.set_yaw(l)
            )
            self.yaw_buttons.append((lvl, btn))
            yaw_controls.append(btn)

        self.yaw_row = ft.Row(yaw_controls, spacing=5, scroll=ft.ScrollMode.AUTO)

        self.yaw_dot = ft.Container(width=16, height=16, border_radius=8, bgcolor=ft.Colors.BLUE, left=self.bar_width/2 - 8, top=2)
        self.yaw_left_thresh = ft.Container(width=2, height=20, bgcolor=ft.Colors.RED, left=self._calc_pos(-self.yaw_threshold_val), top=0)
        self.yaw_right_thresh = ft.Container(width=2, height=20, bgcolor=ft.Colors.RED, left=self._calc_pos(self.yaw_threshold_val), top=0)
        self.yaw_center = ft.Container(width=2, height=20, bgcolor=ft.Colors.BLACK_54, left=self.bar_width/2 - 1, top=0)

        self.yaw_bar = ft.Stack([
            ft.Container(width=self.bar_width, height=20, bgcolor=ft.Colors.GREY_200, border_radius=10),
            self.yaw_center,
            self.yaw_left_thresh,
            self.yaw_right_thresh,
            self.yaw_dot
        ], width=self.bar_width, height=20)

        # Build Page Layout
        self.content = ft.Column([
            ft.Text("Head Movement Thresholds", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_87),
            ft.Text("Select a threshold value (1-17). When the blue dot (your head) passes the red line, the event triggers.", color=ft.Colors.BLACK_54),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            
            self.create_card("Pitch / Vertical (Used for Scrolling Up & Down)", ft.Icons.SWAP_VERT, [
                ft.Row([self.pitch_text, self.pitch_status], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=400),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.pitch_bar,
                ft.Row([ft.Text("Down", size=12), ft.Text("Center", size=12), ft.Text("Up", size=12)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=400),
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                self.pitch_val_text,
                self.pitch_row
            ]),
            
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),

            self.create_card("Yaw / Horizontal (Used for Left & Right)", ft.Icons.SWAP_HORIZ, [
                ft.Row([self.yaw_text, self.yaw_status], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=400),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.yaw_bar,
                ft.Row([ft.Text("Left", size=12), ft.Text("Center", size=12), ft.Text("Right", size=12)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=400),
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                self.yaw_val_text,
                self.yaw_row
            ])
        ], scroll=ft.ScrollMode.AUTO)

    # ==========================================
    # HELPER METHODS
    # ==========================================
    def create_card(self, title, icon, controls):
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icon, color=ft.Colors.BLUE_600), ft.Text(title, size=18, weight=ft.FontWeight.BOLD)]),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                *controls
            ]),
            padding=24, bgcolor=ft.Colors.WHITE, border_radius=12,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.BLACK_12), right=ft.BorderSide(1, ft.Colors.BLACK_12), bottom=ft.BorderSide(1, ft.Colors.BLACK_12), left=ft.BorderSide(1, ft.Colors.BLACK_12)),
            shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.BLACK_12)
        )

    def _calc_pos(self, angle):
        """Converts an angle into a pixel position on the 400px wide bar."""
        clamped_angle = max(-self.max_angle, min(self.max_angle, angle))
        return (self.bar_width / 2) + (clamped_angle * (self.bar_width / (self.max_angle * 2)))

    # --- BUTTON LOGIC FOR PITCH ---
    def set_pitch(self, level):
        self.pitch_threshold_val = float(level)
        if self.mouse_controller:
            self.mouse_controller.scroll_threshold = self.pitch_threshold_val
            
        # Update text
        self.pitch_val_text.value = f"Pitch Threshold: Current Value ({self.pitch_threshold_val:.1f}°)"
        self.pitch_val_text.update()
        
        # Update bar red lines
        self.pitch_left_thresh.left = self._calc_pos(-self.pitch_threshold_val)
        self.pitch_right_thresh.left = self._calc_pos(self.pitch_threshold_val)
        self.pitch_bar.update()

        # Update button colors
        for lvl, btn in self.pitch_buttons:
            is_active = (lvl == level)
            btn.bgcolor = ft.Colors.BLUE_50 if is_active else ft.Colors.BLUE_GREY_50
            btn.color = ft.Colors.BLUE_900 if is_active else ft.Colors.BLACK_87
            btn.update()

    # --- BUTTON LOGIC FOR YAW ---
    def set_yaw(self, level):
        self.yaw_threshold_val = float(level)
        
        # Update text
        self.yaw_val_text.value = f"Yaw Threshold: Current Value ({self.yaw_threshold_val:.1f}°)"
        self.yaw_val_text.update()
        
        # Update bar red lines
        self.yaw_left_thresh.left = self._calc_pos(-self.yaw_threshold_val)
        self.yaw_right_thresh.left = self._calc_pos(self.yaw_threshold_val)
        self.yaw_bar.update()

        # Update button colors
        for lvl, btn in self.yaw_buttons:
            is_active = (lvl == level)
            btn.bgcolor = ft.Colors.BLUE_50 if is_active else ft.Colors.BLUE_GREY_50
            btn.color = ft.Colors.BLUE_900 if is_active else ft.Colors.BLACK_87
            btn.update()

    def update_live_data(self, pitch, yaw):
        """Called by the camera thread to visually move the dots."""
        if not self.page: return # Ignore if the tab is hidden

        # Since scrolling locks a "baseline", we calculate the live difference for Pitch
        display_pitch = pitch
        if self.mouse_controller and self.mouse_controller.scroll_baseline_pitch is not None:
            display_pitch = pitch - self.mouse_controller.scroll_baseline_pitch

        self.pitch_dot.left = self._calc_pos(display_pitch) - 8 
        self.yaw_dot.left = self._calc_pos(yaw) - 8

        self.pitch_text.value = f"Current Pitch: {display_pitch:.1f}°"
        self.yaw_text.value = f"Current Yaw: {yaw:.1f}°"

        # Highlight Pitch Events
        if display_pitch > self.pitch_threshold_val:
            self.pitch_status.value = "EXECUTING UP!"
            self.pitch_status.color = ft.Colors.GREEN
        elif display_pitch < -self.pitch_threshold_val:
            self.pitch_status.value = "EXECUTING DOWN!"
            self.pitch_status.color = ft.Colors.GREEN
        else:
            self.pitch_status.value = "IDLE"
            self.pitch_status.color = ft.Colors.GREY

        # Highlight Yaw Events
        if yaw > self.yaw_threshold_val:
            self.yaw_status.value = "EXECUTING RIGHT!"
            self.yaw_status.color = ft.Colors.GREEN
        elif yaw < -self.yaw_threshold_val:
            self.yaw_status.value = "EXECUTING LEFT!"
            self.yaw_status.color = ft.Colors.GREEN
        else:
            self.yaw_status.value = "IDLE"
            self.yaw_status.color = ft.Colors.GREY

        try:
            self.pitch_text.update()
            self.pitch_status.update()
            self.pitch_bar.update()
            self.yaw_text.update()
            self.yaw_status.update()
            self.yaw_bar.update()
        except Exception:
            pass 