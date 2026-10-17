import flet as ft
import cv2
import base64
import asyncio
import time

# Notice we don't need pyautogui here anymore, because GestureExecutor handles it!
from gesture_control import GestureExecutor, GestureMouseController
from gesture_control import FaceGestureDetection

class CameraPage(ft.Container):
    def __init__(self, main_page: ft.Page, mouse_bindings_page=None):
        super().__init__()
        self.main_page = main_page
        self.mouse_bindings_page = mouse_bindings_page
        self.expand = True
        self.padding = 30
        self.bgcolor = ft.Colors.TRANSPARENT

        self.mouse_controller = GestureMouseController()
        self.gesture_detector = FaceGestureDetection()

        # Initialize the executor and pass the Flet GUI page so it can read your settings
        self.executor = GestureExecutor(self)
        
        self.cam_image = ft.Image(
            src="", 
            width=640, 
            height=480, 
            fit="cover", 
            border_radius=10,
            gapless_playback=True 
        )
        
        self.camera_card = ft.Container(
            content=self.cam_image, 
            padding=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            border=ft.Border(
                top=ft.BorderSide(1, ft.Colors.BLACK_12),
                right=ft.BorderSide(1, ft.Colors.BLACK_12),
                bottom=ft.BorderSide(1, ft.Colors.BLACK_12),
                left=ft.BorderSide(1, ft.Colors.BLACK_12)
            ),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.Colors.BLUE_GREY_100)
        )
        
        self.start_btn = ft.Button(
            content="Start", 
            icon=ft.Icons.PLAY_ARROW, 
            bgcolor=ft.Colors.GREEN, 
            color=ft.Colors.WHITE, 
            on_click=self.start_camera_click
        )
        
        self.stop_btn = ft.Button(
            content="Stop", 
            icon=ft.Icons.STOP, 
            bgcolor=ft.Colors.RED, 
            color=ft.Colors.WHITE, 
            on_click=self.stop_camera_click, 
            disabled=True
        )

        self.content = ft.Column([
            ft.Text("Camera", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_87),
            ft.Text("Camera Section", color=ft.Colors.BLACK_54),
            ft.Container(height=10),
            ft.Row([self.start_btn, self.stop_btn]),
            ft.Container(height=10),
            self.camera_card
        ], horizontal_alignment=ft.CrossAxisAlignment.START)

        self.cap = None
        self.is_running = False

    def start_camera_click(self, e):
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.update()
        self.start_camera()

    def stop_camera_click(self, e):
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.update()
        self.stop_camera()

    def start_camera(self):
        if self.is_running:
            return
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

        # CAP_MSMF is capture at the windows
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

    async def update_frame(self):
        print("[CAM]Image stream started (Async Mode)...")
        
        while self.is_running:
            if self.cap is None or not self.cap.isOpened():
                break
                
            ret, frame = self.cap.read()
            if not ret or frame is None:
                await asyncio.sleep(0.1)
                continue
        
            small_frame = cv2.resize(frame, (480, 360))
            _, buffer = cv2.imencode('.jpg', small_frame, [cv2.IMWRITE_JPEG_QUALITY, 50]) 
            base64_str = base64.b64encode(buffer).decode("utf-8")
            
            self.cam_image.src = f"data:image/jpeg;base64,{base64_str}"

            frame = self.mouse_controller.process_frame(frame)

            # 1. Detect the gesture string (e.g. "left_wink")
            detected_gesture = self.gesture_detector.detect(frame)

            # 2. Pass it directly to the dynamic executor!
            if detected_gesture:
                self.executor.handle_gesture(detected_gesture)
            
            try:
                self.cam_image.update()
            except Exception:
                pass

            # --- FEED LIVE DATA TO GESTURE UI AND DESKTOP ---
            if hasattr(self.executor, 'app'):
                p = getattr(self.mouse_controller, 'latest_pitch', 0)
                y = getattr(self.mouse_controller, 'latest_yaw', 0)
                
                # If scrolling, show the difference from the baseline
                is_scroll = getattr(self.mouse_controller, 'is_scrolling', False)
                if is_scroll and getattr(self.mouse_controller, 'scroll_baseline_pitch', None) is not None:
                    p = p - self.mouse_controller.scroll_baseline_pitch

                if hasattr(self.executor.app, 'gesture_determine_page'):
                    self.executor.app.gesture_determine_page.update_live_data(p, y)
                    
                if hasattr(self.executor.app, 'desktop_page') and hasattr(self.executor.app.desktop_page, 'update_live_data'):
                    mode = self.executor.get_current_mode_name()
                    method = "none"
                    if hasattr(self.executor.app, 'mouse_bindings_page'):
                        method = self.executor.app.mouse_bindings_page.active_click_method
                    
                    # Safely pass exactly 5 core arguments to the desktop
                    self.executor.app.desktop_page.update_live_data(p, y, mode, method, is_scroll)
            
            await asyncio.sleep(0.04)
            
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            print("[CAM]Camera hardware successfully released.")