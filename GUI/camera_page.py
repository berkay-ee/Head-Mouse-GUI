import flet as ft
import cv2
import base64
import asyncio
import time
import pyautogui  # Centering the cursor requires pyautogui for direct mouse control

# Hud widget import for window mode
from widget import MiniHUD

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

        # Start button for starting the camera feed
        self.start_btn = ft.Button("Start", icon=ft.Icons.PLAY_ARROW, bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE, on_click=self.start_camera_click)
        # Stop button for stopping the camera feed
        self.stop_btn = ft.Button("Stop", icon=ft.Icons.STOP, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE, on_click=self.stop_camera_click, disabled=True)
        # Mini HUD Mode button for toggling the HUD window
        self.hud_btn = ft.Button("Mini HUD Mode", icon=ft.Icons.PICTURE_IN_PICTURE_ALT, bgcolor=ft.Colors.BLUE_ACCENT, color=ft.Colors.WHITE, on_click=self.toggle_hud_mode, disabled=True)
        
        # Recalibrate button for centering the cursor
        self.recalibrate_btn = ft.Button("Cursor Calibrate", icon=ft.Icons.CENTER_FOCUS_STRONG, bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE, on_click=self.recalibrate_click, disabled=True)

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
            
            # Buttons for controlling the camera and HUD
            ft.Row([self.start_btn, self.stop_btn, self.hud_btn, self.recalibrate_btn], wrap=True),
            
            ft.Container(height=10),
            self.camera_card
        ], horizontal_alignment=ft.CrossAxisAlignment.START)

    # =========================================================================
    # RECALIBRATE (MERKEZLEME) FONKSİYONU - 5 seconds countdown
    # =========================================================================
    def recalibrate_click(self, e):
        # Start the recalibration process in the mouse controller
        if hasattr(self.mouse_controller, 'trigger_calibration'):
            self.mouse_controller.trigger_calibration()
        else:
            print("[HATA] trigger_calibration fonksiyonu GestureMouseController içinde bulunamadı!")

        # Show a snack bar notification for recalibration countdown
        self.main_page.snack_bar = ft.SnackBar(
            content=ft.Text("Calibrating...", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            bgcolor=ft.Colors.ORANGE_700,
            duration=5000  # Recalibration countdown duration
        )
        self.main_page.snack_bar.open = True
        self.main_page.update()

    def start_camera_click(self, e):
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.hud_btn.disabled = False 
        self.recalibrate_btn.disabled = False # Activate recalibrate button when camera is running
        self.update()
        self.start_camera()

    def stop_camera_click(self, e):
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.hud_btn.disabled = True 
        self.recalibrate_btn.disabled = True # Camera is stopped, disable recalibrate
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
            self.recalibrate_btn.disabled = False
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
            self.recalibrate_btn.disabled = True
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
            
            # Widget size configurations for HUD mode
            self.main_page.window.width = 250  #HUD window width 
            self.main_page.window.height = 320 #HUD window height 
            self.main_page.window.frameless = False  # Add a frame to the HUD window for close or minimize buttons
            self.main_page.window.always_on_top = True  # HUD window stays on top of other windows

            self.main_page.window.bgcolor = ft.Colors.TRANSPARENT # Set the background color to transparent for the HUD window
            self.main_page.bgcolor = ft.Colors.TRANSPARENT # Set the background color to transparent for the main page
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

            # ===============================================================
            # 1. Mouse Conttroler and Gesture Detection
            # ===============================================================
            frame = self.mouse_controller.process_frame(frame)
            detected_gesture = self.gesture_detector.detect(frame)

            if detected_gesture:
                self.executor.handle_gesture(detected_gesture)

            # ===============================================================
            # 2. Update the camera feed in the UI
            # ===============================================================
            small_frame = cv2.resize(frame, (480, 360))
            _, buffer = cv2.imencode('.jpg', small_frame, [cv2.IMWRITE_JPEG_QUALITY, 50]) 
            base64_str = base64.b64encode(buffer).decode("utf-8")
            
            self.cam_image.src = f"data:image/jpeg;base64,{base64_str}"

            try:
                self.cam_image.update()
            except Exception:
                pass

            # ===============================================================
            # 3. Update HUD and Desktop Page with Live Data
            # ===============================================================
            if hasattr(self.executor, 'app'):
                p = getattr(self.mouse_controller, 'latest_pitch', 0)
                y = getattr(self.mouse_controller, 'latest_yaw', 0)
                
                is_scroll = getattr(self.mouse_controller, 'is_scrolling', False)
                if is_scroll and getattr(self.mouse_controller, 'scroll_baseline_pitch', None) is not None:
                    p = p - self.mouse_controller.scroll_baseline_pitch

                mode_display = self.executor.get_current_mode_name()

                if getattr(self, 'is_hud_mode', False) and hasattr(self, 'hud_widget'):
                    # 1. Varsayılan değerler
                    ble_stat, x_val, y_val, dwell_stat, dwell_time_val = "-", "-", "-", "OFF", "-"
                    
                    try:
                        # 2. BLE Durumunu Arayüzden Değil, Doğrudan BLE Yöneticisinden Oku
                        if hasattr(self.executor, 'ble_manager'):
                            # Kendi BLE değişkeninize göre 'is_connected' adını düzenleyebilirsiniz
                            is_conn = getattr(self.executor.ble_manager, 'is_connected', False)
                            ble_stat = "Connected" if is_conn else "Disconnected"
                        elif hasattr(self.executor.app, 'desktop_page'): 
                            # BLE manager bulunamazsa son çare eski yöntemle bak
                            ble_stat = getattr(self.executor.app.desktop_page, 'status_text', type('obj', (object,), {'value': '-'})).value

                        # 3. Hız ve Oto Tık Ayarlarını Arayüzden Değil, Doğrudan Ayar Sayfasından Oku
                        if hasattr(self.executor.app, 'mouse_bindings_page'):
                            mbp = self.executor.app.mouse_bindings_page
                            
                            # DİKKAT: Projenizdeki asıl değişken adları farklıysa (örneğin horizontal_speed yerine speed_x ise) burayı güncelleyin!
                            x_val = str(getattr(mbp, 'horizontal_speed', x_val))
                            y_val = str(getattr(mbp, 'vertical_speed', y_val))
                            
                            dwell_enabled = getattr(mbp, 'dwell_click_enabled', False) # veya dwell_enabled
                            dwell_stat = "ON" if dwell_enabled else "OFF"
                            
                            dwell_time_val = str(getattr(mbp, 'dwell_time', dwell_time_val))

                    except Exception as e:
                        print(f"Arka Plandan Veri Çekme Hatası: {e}")

                    # 4. Çekilen gerçek verilerle HUD'u güncelle
                    print(f"HUD DEBUG: P:{p}, Y:{y}, BLE:{ble_stat}, X:{x_val}, Dwell:{dwell_stat}")
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