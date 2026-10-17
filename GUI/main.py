import flet as ft
from side_bar import Sidebar
from desktop import DesktopPage
from camera_page import CameraPage

from CamCursor_control import CursorControlPage

from mouse_bindings import MouseBindingsPage
from dwell_clicker import DwellClicker

from apps import AppsPage


# Ram test libary
import psutil
import threading
import time
import matplotlib.pyplot as plt


class SensePilotApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        
        # ==========================================
        # Create the pages and components
        # ==========================================
    
        from dwell_clicker import DwellClicker
        self.dwell_clicker = DwellClicker()

        # 2. Create mouse bindings page FIRST so other pages can reference it
        from mouse_bindings import MouseBindingsPage
        self.mouse_bindings_page = MouseBindingsPage(dwell_clicker=self.dwell_clicker)

                # 3. Create camera page and pass the mouse bindings page into it
        from camera_page import CameraPage
        self.camera_page = CameraPage(self.page, mouse_bindings_page=self.mouse_bindings_page)

        from gesture_determine import GestureDeterminePage
        self.gesture_determine_page = GestureDeterminePage(mouse_controller=self.camera_page.mouse_controller)



        # Third, create the desktop page 
        from desktop import DesktopPage

        self.apps_page = AppsPage(page)

        self.desktop_page = DesktopPage(
            mouse_controller=self.camera_page.mouse_controller,
            dwell_clicker=self.dwell_clicker,
            on_ble_connected_callback=self.stop_camera_if_running
        )

        # Fourth, create the remaining setting pages
        from mouse_bindings import MouseBindingsPage
        self.mouse_bindings_page = MouseBindingsPage(dwell_clicker=self.dwell_clicker)

        from CamCursor_control import CursorControlPage
        self.cursor_control_page = CursorControlPage(mouse_controller=self.camera_page.mouse_controller)
        
        
        # --- Content Area ---
        self.content_area = ft.Container(
            content=self.desktop_page, # Start with a desktop page
            padding=30,
            expand=True,
            bgcolor=ft.Colors.WHITE
        )
        
        # --- Sol Menü (Sidebar) ---
        from side_bar import Sidebar
        self.sidebar = Sidebar(on_menu_click=self.change_page)
        
        self.page.add(
            ft.Row([
                self.sidebar,
                self.content_area
            ], expand=True, spacing=0)
        )

    def stop_camera_if_running(self):
        # Stop the camera if we are on the Camera page and it's running
        if hasattr(self, 'camera_page') and self.camera_page is not None:
            if self.camera_page.is_running:
                #self.camera_page.start_btn.disabled = False
                #self.camera_page.stop_btn.disabled = True
                #self.camera_page.update()
                self.camera_page.stop_camera()

    # upper bar setup
    def setup_page(self):
        self.page.title = "PixelPilot - Head Mouse Control"
        self.page.padding = 0
        self.page.window_width = 1100
        self.page.window_height = 700
        self.page.bgcolor = ft.Colors.WHITE

   
    def change_page(self, route):
        
        # Stop BLE connection if we are leaving the Desktop page
        if route != "Desktop":
            if hasattr(self, 'desktop_page') and self.desktop_page is not None:
                self.desktop_page.stop_ble()
       
        #  Switch to the selected page desktop page
        if route == "Desktop":
            if hasattr(self, 'desktop_page'):
                self.desktop_page.update_dashboard()
            self.content_area.content = self.desktop_page
            
        elif route == "PixelPilot" or route == "PixelPilot ": 
            self.content_area.content = ft.Text("Mouse setting loading", size=20)

        
        elif route == "Camera":

            # self.camera_page = CameraPage(self.page)
            
            # New page
            self.content_area.content = self.camera_page

        elif route == "CursorControl" or route == "Cursor Control":
            self.content_area.content = self.cursor_control_page
            
        elif route == "MouseBindings" or route == "Mouse Bindings":
            # Update the active mode text in the mouse bindings page based on the current mode from the camera page's executor
            if hasattr(self, 'camera_page') and hasattr(self.camera_page, 'executor'):
                current_mode = self.camera_page.executor.get_current_mode_name()
                if hasattr(self, 'mouse_bindings_page'):
                    self.mouse_bindings_page.update_active_mode_text(current_mode)
            # -----------------------------------
            self.content_area.content = self.mouse_bindings_page

        elif route == "Apps" or route == "Apps Page": 
            self.content_area.content = self.apps_page

        elif route == "FaceGesture" or route == "Face Gesture":
         self.content_area.content = self.gesture_determine_page

        else:
            self.content_area.content = ft.Text(f"{route} Ekranı", size=20)
            
        self.page.update()


def monitor_system_usage(duration_seconds=60):
    process = psutil.Process()
    # Automatically detects your 16 logical cores for accurate math
    logical_cores = psutil.cpu_count(logical=True) 
    
    cpu_records = []
    ram_records = []
    time_axis = list(range(duration_seconds))
    
    print(f"\n[System] Hardware detected: {logical_cores} logical threads.")
    print(f"[System] Starting {duration_seconds}-second benchmark. Move your head and switch apps!")
    
    for _ in range(duration_seconds):
        # Fetch the raw CPU load and normalize it based on your i5-13450HX architecture
        raw_cpu = process.cpu_percent(interval=1.0)
        normalized_cpu = raw_cpu / logical_cores
        cpu_records.append(normalized_cpu)
        
        # Record RAM
        ram_mb = process.memory_info().rss / (1024 * 1024)
        ram_records.append(ram_mb)

    avg_cpu = sum(cpu_records) / len(cpu_records)
    peak_ram = max(ram_records)
    
    print("\n--- BENCHMARK RESULTS FOR ABSTRACT ---")
    print(f"Average CPU Utilization: {avg_cpu:.1f}%")
    print(f"Peak Memory (RAM) Footprint: {peak_ram:.1f} MB")
    print("--------------------------------------\n")
    
    # ==========================================
    # Generate Academic Graph
    # ==========================================
    plt.figure(figsize=(8, 5))
    
    # Top subplot: CPU
    plt.subplot(2, 1, 1)
    plt.plot(time_axis, cpu_records, color='#1f77b4', linewidth=2, label='CPU Usage')
    plt.ylabel('CPU Usage (%)', fontweight='bold')
    
    # Forces the Y-axis to scale normally from 0 to at least 100%
    max_y = max(100, max(cpu_records) + 10)
    plt.ylim(0, max_y)
    
    
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper right')
    
    # Bottom subplot: RAM
    plt.subplot(2, 1, 2)
    plt.plot(time_axis, ram_records, color='#d62728', linewidth=2, label='RAM Footprint')
    plt.xlabel('Time (Seconds)', fontweight='bold')
    plt.ylabel('Memory (MB)', fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper right')
    
    plt.tight_layout()
    
    # Save as a high-res PDF for LaTeX
    plt.savefig('system_performance.pdf', format='pdf', dpi=300)
    print("[Graph] Saved successfully as 'system_performance.pdf'")
    

def main(page: ft.Page):
    app = SensePilotApp(page)
    
    # Start the benchmark in the background as soon as the app loads
    threading.Thread(target=monitor_system_usage, args=(60,), daemon=True).start()

# start the app
if __name__ == "__main__":
    ft.run(main)