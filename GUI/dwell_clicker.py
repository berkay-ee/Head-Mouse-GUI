import threading
import time
import math
import tkinter as tk
import ctypes
import pyautogui

# Prevent the hidden clicker thread from crashing if it hits the screen corners
pyautogui.FAILSAFE = False

class DwellClicker:
    def __init__(self):
        # Starts OFF so your GUI (Mouse Bindings page) can control it
        self.enabled = False 
        
        self.dwell_time = 1.5      # Can be changed by the GUI
        self.click_radius = 20     # Wiggle room for the cursor
        self.is_running = True
        
        # Start the visual overlay loop in the background
        self.thread = threading.Thread(target=self._run_overlay, daemon=True)
        self.thread.start()

    def _set_clickthrough(self, hwnd):
        """Makes the Tkinter window completely transparent to clicks"""
        try:
            WS_EX_TRANSPARENT = 0x00000020
            WS_EX_LAYERED = 0x00080000
            GWL_EXSTYLE = -20
            user32 = ctypes.windll.user32
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT)
        except Exception as e:
            print(f"[DwellClicker] Clickthrough setup error: {e}")

    def _run_overlay(self):
        # Set the process to be DPI aware to prevent scaling issues on high-DPI displays
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except:
            pass

        self.root = tk.Tk()
        self.root.overrideredirect(True) # Borderless Window
        self.root.attributes("-topmost", True) 
        self.root.attributes("-transparentcolor", "black") # Black transparent background
        self.root.config(bg="black")
        self.root.geometry("100x100+-200+-200") # Start off-screen
        
        self.root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        if not hwnd:
            hwnd = self.root.winfo_id()
        self._set_clickthrough(hwnd)
        
        self.canvas = tk.Canvas(self.root, width=100, height=100, bg="black", highlightthickness=0)
        self.canvas.pack()
        
        # Create the visual circle (starts empty/invisible)
        self.arc = self.canvas.create_arc(10, 10, 90, 90, start=90, extent=0, outline="#00ff00", width=6, style=tk.ARC)
        
        self.last_x, self.last_y = pyautogui.position()
        self.dwell_start = time.time()
        self.clicked = False
        
        self._update_loop()
        self.root.mainloop()

    def _update_loop(self):
        # 1. Check if the app is shutting down
        if not self.is_running:
            self.root.destroy()
            return

        # 2. Check if the GUI turned the auto-clicker OFF
        if not self.enabled:
            self.canvas.itemconfig(self.arc, extent=0)
            self.root.geometry("10x10+-200+-200") # Move off screen
            self.root.after(100, self._update_loop)
            return

        # 3. Dwell logic
        try:
            curr_x, curr_y = pyautogui.position()
            dist = math.hypot(curr_x - self.last_x, curr_y - self.last_y)

            # If mouse moves outside the tolerance radius, reset the timer
            if dist > self.click_radius:
                self.last_x, self.last_y = curr_x, curr_y
                self.dwell_start = time.time()
                self.clicked = False
                self.canvas.itemconfig(self.arc, extent=0)
                self.root.geometry("10x10+-200+-200") 
            else:
                # If cursor is stable...
                if not self.clicked:
                    elapsed = time.time() - self.dwell_start
                    # GUI controls self.dwell_time!
                    progress = min(1.0, elapsed / self.dwell_time) 
                    
                    # Wait 100ms before showing the UI to prevent flickering
                    if elapsed > 0.1:
                        # Center the circle on the mouse
                        self.root.geometry(f"100x100+{curr_x - 50}+{curr_y - 50}")
                        
                        # Grow the circle based on time
                        extent = -360 * progress
                        self.canvas.itemconfig(self.arc, extent=extent)
                        
                        # Change color to red right before clicking
                        color = "#ff3300" if progress > 0.8 else "#00ff00"
                        self.canvas.itemconfig(self.arc, outline=color)

                    # Click time is up!
                    if progress >= 1.0:
                        self.canvas.itemconfig(self.arc, extent=0)
                        self.root.geometry("10x10+-200+-200") 
                        self.root.update()
                        
                        pyautogui.click()
                        self.clicked = True # Prevent machine-gun clicking
                        
        except Exception as e:
            print(f"[DwellClicker Error]: {e}")
        
        # Loop again
        self.root.after(30, self._update_loop)