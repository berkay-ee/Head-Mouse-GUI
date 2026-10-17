import cv2
import pyautogui
import time
import mediapipe as mp
import math
import numpy as np
import flet as ft
from OneEuroFilter import OneEuroFilter
import math

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0  # Removes the 100ms Windows delay limit

class FaceGestureDetection:
    """
    Analyzes facial landmarks to detect specific gestures (winks and mouth open).
    """
    def __init__(self, blink_threshold=0.10, mouth_open_threshold=0.04, cooldown=0.6):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True, 
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        self.blink_threshold = blink_threshold
        self.mouth_threshold = mouth_open_threshold
        self.last_detection_time = 0
        self.cooldown = cooldown  

    def _calculate_ear(self, landmarks, side="left"):
        if side == "left":
            upper, lower = landmarks[159], landmarks[145]
            outer, inner = landmarks[33], landmarks[133]
        else:
            upper, lower = landmarks[386], landmarks[374]
            outer, inner = landmarks[263], landmarks[362]

        vertical_dist = math.hypot(upper.x - lower.x, upper.y - lower.y)
        horizontal_dist = math.hypot(outer.x - inner.x, outer.y - inner.y)
        if horizontal_dist == 0: return 1.0
        return vertical_dist / horizontal_dist

    def detect(self, frame):
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                current_time = time.time()
                
                if current_time - self.last_detection_time > self.cooldown:
                    left_ear = self._calculate_ear(landmarks, "left")
                    right_ear = self._calculate_ear(landmarks, "right")
                    
                    left_is_closed = left_ear < self.blink_threshold
                    right_is_closed = right_ear < self.blink_threshold

                    upper_lip, lower_lip = landmarks[13], landmarks[14]
                    mouth_dist = math.hypot(upper_lip.x - lower_lip.x, upper_lip.y - lower_lip.y)
                    mouth_is_open = mouth_dist > self.mouth_threshold

                    if left_is_closed and not right_is_closed:
                        self.last_detection_time = current_time
                        return "left_wink"
                    elif right_is_closed and not left_is_closed:
                        self.last_detection_time = current_time
                        return "right_wink"
                    elif left_is_closed and right_is_closed:
                        self.last_detection_time = current_time
                        return "both_blink"
                    elif mouth_is_open:
                        self.last_detection_time = current_time
                        return "mouth_open"
                        
        except Exception as e:
            print(f"[ERR] Gesture detection error: {e}")
        return None  


class GestureExecutor:
    """
    Handles mode switching and triggers system mouse events or keyboard shortcuts.
    """
    def __init__(self, main_app_instance):
        self.app = main_app_instance
        self.cycle_modes = ["Left Click", "Right Click", "Double Click", "Scroll Mode", "App Switcher"]
        self.current_mode_index = 0
        
        if hasattr(self.app, 'dwell_clicker') and self.app.dwell_clicker:
            self.app.dwell_clicker.on_click_callback = self.execute_active_mode

    def get_current_mode_name(self):
        if self.current_mode_index < len(self.cycle_modes):
            return self.cycle_modes[self.current_mode_index]
        return "Left Click"

    def handle_gesture(self, detected_gesture):
        if not detected_gesture:
            return

        if detected_gesture == "mouth_open":
            self.current_mode_index += 1
            if self.current_mode_index >= len(self.cycle_modes):
                self.current_mode_index = 0
            
            mode_name = self.cycle_modes[self.current_mode_index]
            print(f"[Gesture] Mode cycled to: {mode_name}")
            
            is_scroll = (mode_name == "Scroll Mode")
            is_app_switch = (mode_name == "App Switcher")
            
            if hasattr(self.app, 'mouse_controller'):
                self.app.mouse_controller.is_scrolling = is_scroll
                self.app.mouse_controller.is_app_switching = is_app_switch
                self.app.mouse_controller.scroll_baseline_pitch = None
                self.app.mouse_controller.switch_baseline_yaw = None
                
            if hasattr(self.app, 'mouse_bindings_page'):
                dwell = self.app.mouse_bindings_page.dwell_clicker
                if dwell and self.app.mouse_bindings_page.active_click_method == "dwell":
                    dwell.enabled = not (is_scroll or is_app_switch)

            if is_app_switch:
                pyautogui.hotkey('win', 'tab')

            if hasattr(self.app, 'mouse_bindings_page'):
                self.app.mouse_bindings_page.update_active_mode_text(mode_name)
            
            if hasattr(self.app, 'desktop_page') and hasattr(self.app.desktop_page, 'val_live_mode'):
                self.app.desktop_page.val_live_mode.value = mode_name.upper()
                
                if is_scroll:
                    self.app.desktop_page.val_live_mode.color = ft.Colors.RED_700
                    self.app.desktop_page.val_live_scroll.value = "SCROLLING (FROZEN)"
                    self.app.desktop_page.val_live_scroll.color = ft.Colors.RED_700
                elif is_app_switch:
                    self.app.desktop_page.val_live_mode.color = ft.Colors.CYAN_700
                    self.app.desktop_page.val_live_scroll.value = "SWITCHING (FROZEN)"
                    self.app.desktop_page.val_live_scroll.color = ft.Colors.CYAN_700
                else:
                    if mode_name == "Left Click": self.app.desktop_page.val_live_mode.color = ft.Colors.GREEN_700
                    elif mode_name == "Right Click": self.app.desktop_page.val_live_mode.color = ft.Colors.PURPLE_700
                    else: self.app.desktop_page.val_live_mode.color = ft.Colors.ORANGE_700
                    
                    self.app.desktop_page.val_live_scroll.value = "OFF (MOVING)"
                    self.app.desktop_page.val_live_scroll.color = ft.Colors.GREY_500
                    
                if self.app.desktop_page.page:
                    try:
                        self.app.desktop_page.val_live_mode.update()
                        self.app.desktop_page.val_live_scroll.update()
                        self.app.desktop_page.update()
                    except Exception:
                        pass
            
            if hasattr(self.app, 'page') and self.app.page:
                try:
                    self.app.page.update()
                except Exception:
                    pass
            return

        if detected_gesture in ["left_wink", "right_wink", "both_blink"]:
            if self.get_current_mode_name() == "App Switcher":
                pyautogui.press('enter')
                print("[Gesture] App Selected! Resetting to Left Click.")
                self.current_mode_index = 0
                
                if hasattr(self.app, 'mouse_controller'):
                    self.app.mouse_controller.is_app_switching = False
                
                if hasattr(self.app, 'mouse_bindings_page'):
                    dwell = self.app.mouse_bindings_page.dwell_clicker
                    if dwell and self.app.mouse_bindings_page.active_click_method == "dwell":
                        dwell.enabled = True
                    self.app.mouse_bindings_page.update_active_mode_text("Left Click")
                
                if hasattr(self.app, 'desktop_page') and hasattr(self.app.desktop_page, 'val_live_mode'):
                    self.app.desktop_page.val_live_mode.value = "LEFT CLICK"
                    self.app.desktop_page.val_live_mode.color = ft.Colors.GREEN_700
                    self.app.desktop_page.val_live_scroll.value = "OFF (MOVING)"
                    self.app.desktop_page.val_live_scroll.color = ft.Colors.GREY_500
                    if self.app.desktop_page.page:
                        try:
                            self.app.desktop_page.update()
                        except Exception:
                            pass
                return

            if hasattr(self.app, 'mouse_bindings_page'):
                if self.app.mouse_bindings_page.active_click_method == "blink":
                    self.execute_active_mode()

    def execute_active_mode(self):
        action = self.cycle_modes[self.current_mode_index]
        if action in ["Scroll Mode", "App Switcher"]:
            return 
            
        print(f"[Executor] Executing: {action}")
        if action == "Left Click": pyautogui.click()
        elif action == "Right Click": pyautogui.rightClick()
        elif action == "Double Click": pyautogui.doubleClick()



class GestureMouseController:
    """
    Tracks head posture using MediaPipe Face Mesh. Math is now perfectly 1:1 mapped 
    to the Flet GUI sliders for Sensitivity, Deadzone, and Smoothing.
    """
    def __init__(self, screen_width=1920, screen_height=1080):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2
        self.current_x = self.center_x
        self.current_y = self.center_y

        self.calibrated = False
        self.baseline_yaw = 0.0
        self.baseline_pitch = 0.0

        # Default values (These will be overwritten by your GUI automatically)
        self.sensitivity_x = 90.0  
        self.sensitivity_y = 60.0  
        self.deadzone_yaw = 1.50        
        self.deadzone_pitch = 1.50        
        self.smoothing_factor = 0.25 
        
        self.is_scrolling = False
        self.scroll_baseline_pitch = None
        self.scroll_threshold = 12.0 
        self.scroll_speed = 75      

        self.is_app_switching = False
        self.switch_baseline_yaw = None
        self.last_switch_time = 0
        self.app_switch_cooldown = 1  
        self.switch_threshold = 15.0     

        # NOTE: OneEuroFilter is DELETED. We now use native GUI smoothing below.

    def process_frame(self, frame):
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    
                    nose = face_landmarks.landmark[1]
                    left_eye = face_landmarks.landmark[33]
                    right_eye = face_landmarks.landmark[263]
                    
                    anchor_x = (left_eye.x + right_eye.x) / 2.0
                    anchor_y = (left_eye.y + right_eye.y) / 2.0
                    
                    # 100.0 Scale mapping. Directly aligns with GUI inputs!
                    raw_yaw_offset = (nose.x - anchor_x) * 100.0
                    raw_pitch_offset = (nose.y - anchor_y) * 100.0

                    if not self.calibrated:
                        self.baseline_yaw = raw_yaw_offset
                        self.baseline_pitch = raw_pitch_offset
                        self.calibrated = True
                        print("[CAM] System Calibrated! Head center is set to Screen Center.")
                        pyautogui.moveTo(self.center_x, self.center_y)

                    yaw = raw_yaw_offset - self.baseline_yaw
                    pitch = raw_pitch_offset - self.baseline_pitch
                    
                    pose_text = f"Pitch:{pitch:.1f} Yaw:{yaw:.1f}"
                    cv2.putText(frame, pose_text, (20, max(20, 30)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                
                    # App Switcher Mode
                    if getattr(self, 'is_app_switching', False):
                        current_time = time.time()
                        if self.switch_baseline_yaw is None:
                            self.switch_baseline_yaw = yaw
                            
                        yaw_diff = yaw - self.switch_baseline_yaw
                        if current_time - self.last_switch_time > self.app_switch_cooldown:
                            if yaw_diff > self.switch_threshold:
                                pyautogui.press('right')
                                self.last_switch_time = current_time
                                self.switch_baseline_yaw = yaw 
                            elif yaw_diff < -self.switch_threshold:
                                pyautogui.press('left')
                                self.last_switch_time = current_time
                                self.switch_baseline_yaw = yaw
                                
                        cv2.putText(frame, "APP SWITCHER - FROZEN", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                        break

                    # Scroll Mode
                    if getattr(self, 'is_scrolling', False):
                        if self.scroll_baseline_pitch is None:
                            self.scroll_baseline_pitch = pitch
                            
                        pitch_diff = pitch - self.scroll_baseline_pitch
                        if pitch_diff > self.scroll_threshold:
                            pyautogui.scroll(self.scroll_speed) 
                        elif pitch_diff < -self.scroll_threshold:
                            pyautogui.scroll(-self.scroll_speed) 
                            
                        cv2.putText(frame, "SCROLL - FROZEN", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        break 

                    self.map_head_to_mouse(yaw, pitch)
                    break 
                        # LIVE DEBUGGER: Proves your GUI sliders are talking to the script
                    debug_text = f"DZ:{float(self.deadzone_yaw):.2f} | Sens:{float(self.sensitivity_x):.1f} | Smooth:{float(self.smoothing_factor):.2f}"
                    cv2.putText(frame, debug_text, (20, max(20, 30)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        except Exception as e:
            print(f"[ERR] Tracking error: {e}")
            
        return frame


    def map_head_to_mouse(self, yaw, pitch):
     

            # 1. DOWNWARD BOOST 
            if pitch > 0:  
                pitch *= 1.3  

            # 2. NON-LINEAR ACCELERATION (Ensures straight diagonal lines)
            magnitude = math.hypot(yaw, pitch)
            if magnitude > 0:
                curved_magnitude = magnitude ** 1.15
                curve_scale = curved_magnitude / magnitude
                yaw *= curve_scale
                pitch *= curve_scale

            # 3. RAW TARGET MAPPING
            target_x = self.center_x - (yaw * float(self.sensitivity_x) * 3.5)
            target_y = self.center_y + (pitch * float(self.sensitivity_y) * 3.5)

            target_x = max(0, min(self.screen_width, target_x))
            target_y = max(0, min(self.screen_height, target_y))

            # 4. VELOCITY-BASED DYNAMIC FILTER (The Deadzone Replacement)
            pixel_velocity = math.hypot(target_x - self.current_x, target_y - self.current_y)
            velocity_factor = min(1.0, (pixel_velocity / 40.0) ** 2)

            # Read your GUI Smoothing Slider safely (This is where the error was!)
            try:
                gui_smooth = float(self.smoothing_factor)
            except (ValueError, TypeError):
                gui_smooth = 0.25

            max_alpha = max(0.2, gui_smooth) 

            # Base alpha is 0.01 (stiff). Velocity shoots up and unlocks it instantly.
            alpha = 0.01 + (velocity_factor * (max_alpha - 0.01))

            # 5. APPLY THE SMOOTHING
            self.current_x = (target_x * alpha) + (self.current_x * (1.0 - alpha))
            self.current_y = (target_y * alpha) + (self.current_y * (1.0 - alpha))

            try:
                pyautogui.moveTo(int(self.current_x), int(self.current_y), duration=0)
            except Exception:
                pass