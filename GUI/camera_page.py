import flet as ft
import cv2
import base64
import asyncio
import time

# HUD bileşenini kendi yazdığımız modülden çekiyoruz!
from widget import MiniHUD

# Notice we don't need pyautogui here anymore, because GestureExecutor handles it!
from gesture_control import GestureExecutor, GestureMouseController
from gesture_control import FaceGestureDetection

class CameraPage(ft.Container):
    def __init__(self, main_page: ft.Page, mouse_bindings_page=None, current_theme=None):
        super().__init__()
        self.main_page = main_page
        self.mouse_bindings_page = mouse_bindings_page
        self.expand = True
        self.padding = 30
        self.bgcolor = ft.Colors.TRANSPARENT

        self.current_theme = current_theme if current_theme else {
            "bg": "#F8FAFC", "surface": "#FFFFFF", "primary": "#2563EB", 
            "text": "#0F172A", "text_secondary": "#64748B", "border": "#E2E8F0"
        }

        self.mouse_controller = GestureMouseController()
        self.gesture_detector = FaceGestureDetection()
        self.executor = GestureExecutor(self)
        
        self.cam_image = ft.Image(
            src="", width=640, height=480, fit="cover", border_radius=10, gapless_playback=True 
        )
        
        self.camera_card = ft.Container(
            content=self.cam_image, padding=10, border_radius=15,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.Colors.BLACK_12)
        )
        
        self.start_btn = ft.Button("Start", icon=ft.Icons.PLAY_ARROW, bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE, on_click=self.start_camera_click)
        self.stop_btn = ft.Button("Stop", icon=ft.Icons.STOP, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE, on_click=self.stop_camera_click, disabled=True)
        self.hud_btn = ft.Button("Mini HUD Modu", icon=ft.Icons.PICTURE_IN_PICTURE_ALT, bgcolor=ft.Colors.BLUE_ACCENT, color=ft.Colors.WHITE, on_click=self.toggle_hud_mode, disabled=True)

        self.cap = None
        self.is_running = False
        
        self.is_hud_mode = False
        self.normal_width = 1000
        self.normal_height = 700

        self.build_ui()

    def apply_theme(self, new_theme):
        self.current_theme = new_theme
        self.build_ui()
        try:
            self.update()
        except Exception:
            pass

    def build_ui(self):
        theme = self.current_theme
        self.camera_card.bgcolor = theme["surface"]
        self.camera_card.border = ft.Border(
            top=ft.BorderSide(1, theme["border"]), right=ft.BorderSide(1, theme["border"]),
            bottom=ft.BorderSide(1, theme["border"]), left=ft.BorderSide(1, theme["border"])
        )

        self.content = ft.Column([
            ft.Text("Camera", size=24, weight=ft.FontWeight.BOLD, color=theme["text"]),
            ft.Text("Live feed and gesture recognition status", color=theme["text_secondary"]),
            ft.Container(height=10),
            ft.Row([self.start_btn, self.stop_btn, self.hud_btn]),
            ft.Container(height=10),
            self.camera_card
        ], horizontal_alignment=ft.CrossAxisAlignment.START)

    def start_camera_click(self, e):
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.hud_btn.disabled = False 
        self.update()
        self.start_camera()

    def stop_camera_click(self, e):
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.hud_btn.disabled = True 
        if self.is_hud_mode:
            self.restore_from_hud()
        self.update()
        self.stop_camera()

    def start_camera(self):
        if self.is_running: return
        print("\n[CAM]Camera starting")
        time.sleep(0.3)
        
        self.cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            print("[CAM]Failed to open camera!")
            return

        self.is_running = True
        if hasattr(self, 'start_btn'):
            self.start_btn.disabled = True
            self.stop_btn.disabled = False
            self.update()

        self.cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
        self.main_page.run_task(self.update_frame)

    def stop_camera(self):
        print("[CAM] Camera stopping...")
        self.is_running = False
        time.sleep(0.4)
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        print("[CAM]Camera stopped successfully.\n")
        if hasattr(self, 'start_btn'):
            self.start_btn.disabled = False
            self.stop_btn.disabled = True
            self.update()

    def toggle_hud_mode(self, e):
        if not self.is_hud_mode:
            self.is_hud_mode = True
            self.normal_width = self.main_page.window.width
            self.normal_height = self.main_page.window.height
            
            for control in self.main_page.controls:
                control.visible = False
            
            self.hud_widget = MiniHUD(on_restore=self.restore_from_hud)
            self.main_page.add(self.hud_widget)
            
            # WIDGET BOYUTU YENİ BİLGİLER SIĞSIN DİYE BÜYÜTÜLDÜ (340x440)
            self.main_page.window.width = 360
            self.main_page.window.height = 450
            self.main_page.window.frameless = True
            self.main_page.window.always_on_top = True
            self.main_page.bgcolor = ft.Colors.TRANSPARENT
            self.main_page.update()

    def restore_from_hud(self):
        self.is_hud_mode = False
        if hasattr(self, 'hud_widget') and self.hud_widget in self.main_page.controls:
            self.main_page.controls.remove(self.hud_widget)
            
        for control in self.main_page.controls:
            control.visible = True
            
        self.main_page.window.width = self.normal_width
        self.main_page.window.height = self.normal_height
        self.main_page.window.frameless = False
        self.main_page.window.always_on_top = False
        self.main_page.bgcolor = None
        
        self.main_page.update()
        try:
            self.update()
        except Exception:
            pass

    async def update_frame(self):
        print("[CAM]Image stream started (Async Mode)...")
        while self.is_running:
            if self.cap is None or not self.cap.isOpened(): break
                
            ret, frame = self.cap.read()
            if not ret or frame is None:
                await asyncio.sleep(0.1)
                continue
        
            small_frame = cv2.resize(frame, (480, 360))
            _, buffer = cv2.imencode('.jpg', small_frame, [cv2.IMWRITE_JPEG_QUALITY, 50]) 
            base64_str = base64.b64encode(buffer).decode("utf-8")
            
            self.cam_image.src = f"data:image/jpeg;base64,{base64_str}"
            frame = self.mouse_controller.process_frame(frame)
            detected_gesture = self.gesture_detector.detect(frame)

            if detected_gesture:
                self.executor.handle_gesture(detected_gesture)
            
            try:
                self.cam_image.update()
            except Exception:
                pass

            if hasattr(self.executor, 'app'):
                p = getattr(self.mouse_controller, 'latest_pitch', 0)
                y = getattr(self.mouse_controller, 'latest_yaw', 0)
                
                is_scroll = getattr(self.mouse_controller, 'is_scrolling', False)
                if is_scroll and getattr(self.mouse_controller, 'scroll_baseline_pitch', None) is not None:
                    p = p - self.mouse_controller.scroll_baseline_pitch

                mode_display = self.executor.get_current_mode_name()

                # ===============================================================
                # MASAÜSTÜ VERİLERİNİ ÇEKİP WIDGET'A GÖNDERME KISMI
                # ===============================================================
                if getattr(self, 'is_hud_mode', False) and hasattr(self, 'hud_widget'):
                    ble_stat, x_val, y_val, dwell_stat, dwell_time_val = "-", "-", "-", "-", "-"
                    
                    if hasattr(self.executor.app, 'desktop_page'):
                        dp = self.executor.app.desktop_page
                        ble_stat = dp.status_text.value
                        
                        # "Level 9 (90.0)" gibi uzun yazıları widgeta sığması için "Level 9" şeklinde kırpıyoruz
                        x_val = dp.val_hor_speed.value.split(" (")[0] if " (" in dp.val_hor_speed.value else dp.val_hor_speed.value
                        y_val = dp.val_ver_speed.value.split(" (")[0] if " (" in dp.val_ver_speed.value else dp.val_ver_speed.value
                        
                        dwell_str = dp.val_dwell_status.value
                        dwell_stat = "ON" if "ON" in dwell_str else "OFF"
                        
                        dwell_time_str = dp.val_dwell_time.value
                        if "(" in dwell_time_str:
                            dwell_time_val = dwell_time_str.split("(")[1].replace(")", "")
                        else:
                            dwell_time_val = dwell_time_str

                    self.hud_widget.update_hud(base64_str, p, y, mode_display, ble_stat, x_val, y_val, dwell_stat, dwell_time_val)

                if hasattr(self.executor.app, 'gesture_determine_page'):
                    self.executor.app.gesture_determine_page.update_live_data(p, y)
                    
                if hasattr(self.executor.app, 'desktop_page') and hasattr(self.executor.app.desktop_page, 'update_live_data'):
                    method = "none"
                    if hasattr(self.executor.app, 'mouse_bindings_page'):
                        method = self.executor.app.mouse_bindings_page.active_click_method
                    self.executor.app.desktop_page.update_live_data(p, y, mode_display, method, is_scroll)
            
            await asyncio.sleep(0.04)
            
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            print("[CAM]Camera hardware successfully released.")