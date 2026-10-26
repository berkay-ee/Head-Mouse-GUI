import flet as ft
from side_bar import Sidebar
from desktop import DesktopPage
from camera_page import CameraPage
from CamCursor_control import CursorControlPage
from mouse_bindings import MouseBindingsPage
from dwell_clicker import DwellClicker
from apps import AppsPage
from gesture_determine import GestureDeterminePage
from template import TemplatePage, COLOR_TEMPLATES

# Ram test library
import psutil
import threading
import time
import matplotlib.pyplot as plt


class SensePilotApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_theme = COLOR_TEMPLATES["light"]
        self.setup_page()

        # ==========================================
        # Sayfaları ve Bileşenleri Oluşturma
        # ==========================================
        self.dwell_clicker = DwellClicker()

        # 1. Mouse bindings
        self.mouse_bindings_page = MouseBindingsPage(dwell_clicker=self.dwell_clicker, current_theme=self.current_theme)

        # 2. Camera page
        # 2. Camera page
        self.camera_page = CameraPage(
            self.page, 
            mouse_bindings_page=self.mouse_bindings_page, 
            current_theme=self.current_theme
        )

        # 3. Gesture page
        self.gesture_determine_page = GestureDeterminePage(
            mouse_controller=self.camera_page.mouse_controller, 
            current_theme=self.current_theme
        )

        # 4. Apps & Desktop pages
        self.apps_page = AppsPage(page, current_theme=self.current_theme)
        self.desktop_page = DesktopPage(
            mouse_controller=self.camera_page.mouse_controller,
            dwell_clicker=self.dwell_clicker,
            on_ble_connected_callback=self.stop_camera_if_running
        )

        # 5. Cursor Control page
        self.cursor_control_page = CursorControlPage(
            mouse_controller=self.camera_page.mouse_controller, 
            current_theme=self.current_theme
        )

        # 6. Template & Palet Sayfası
        self.template_page = TemplatePage(
            on_theme_select=self.apply_theme,
            on_preset_select=self.apply_preset,
            current_theme_key="light"
        )

        # --- Content Area ---
        self.content_area = ft.Container(
            content=self.desktop_page,
            padding=30,
            expand=True,
            bgcolor=self.current_theme["bg"]
        )

        # --- Sol Menü (Sidebar) ---
        self.sidebar = Sidebar(on_menu_click=self.change_page, current_theme=self.current_theme)

        # ANA YAPIYI DEĞİŞTİREBİLMEK İÇİN BİR DEĞİŞKENE ATIYORUZ
        self.main_layout = ft.Row([
            self.sidebar,
            self.content_area
        ], expand=True, spacing=0)
        
        self.page.add(self.main_layout)

    def setup_page(self):
        self.page.title = "PixelPilot - Head Mouse Control"
        self.page.padding = 0
        self.page.window_width = 1100
        self.page.window_height = 700
        self.page.theme_mode = self.current_theme["theme_mode"]
        self.page.bgcolor = self.current_theme["bg"]

    def apply_theme(self, theme_dict: dict):
        """Kullanıcı bir palet seçtiğinde tüm sayfanın temasını anlık günceller."""
        self.current_theme = theme_dict
        self.page.theme_mode = theme_dict["theme_mode"]
        self.page.bgcolor = theme_dict["bg"]
        self.content_area.bgcolor = theme_dict["bg"]
        
        # Sidebar with the new theme
        self.sidebar = Sidebar(on_menu_click=self.change_page, current_theme=self.current_theme)
        # Ana layout'un sol menüsünü güncelle
        self.main_layout.controls[0] = self.sidebar

        if hasattr(self, 'desktop_page'):
            self.desktop_page.apply_theme(theme_dict)
        # Şablon sayfasındaki kart sınırlarını tazelemek için içeriği yeniden yükle
        if hasattr(self, 'mouse_bindings_page'):
            self.mouse_bindings_page.apply_theme(theme_dict)
        # cursor control page template card border update
        if hasattr(self, 'cursor_control_page'):
            self.cursor_control_page.apply_theme(theme_dict)

        # camera page theme update
        if hasattr(self, 'camera_page'):
            self.camera_page.apply_theme(theme_dict)    

        # gesture page theme update
        if hasattr(self, 'gesture_determine_page'):
            self.gesture_determine_page.apply_theme(theme_dict)

        # apps page theme update
        if hasattr(self, 'apps_page'):
            self.apps_page.apply_theme(theme_dict)
        
        self.template_page = TemplatePage(
            on_theme_select=self.apply_theme,
            on_preset_select=self.apply_preset,
            current_theme_key=theme_dict["id"]
        )
        if self.content_area.content == self.template_page or isinstance(self.content_area.content, TemplatePage):
            self.content_area.content = self.template_page

        self.page.update()

    def apply_preset(self, preset_dict: dict):
        """Kullanıcı bir imleç hassasiyet şablonu seçtiğinde çalışır."""
        if hasattr(self.camera_page, 'mouse_controller') and self.camera_page.mouse_controller is not None:
            if hasattr(self.camera_page.mouse_controller, 'speed'):
                self.camera_page.mouse_controller.speed = preset_dict.get("speed", 5)

        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"'{preset_dict['name']}' profili yüklendi! (Hız: {preset_dict['speed']}x)"),
            bgcolor=self.current_theme["primary"]
        )
        self.page.snack_bar.open = True
        self.page.update()

    def stop_camera_if_running(self):
        if hasattr(self, 'camera_page') and self.camera_page is not None:
            if self.camera_page.is_running:
                self.camera_page.stop_camera()

    def change_page(self, route):
        if route != "Desktop":
            if hasattr(self, 'desktop_page') and self.desktop_page is not None:
                self.desktop_page.stop_ble()

        if route == "Desktop":
            if hasattr(self, 'desktop_page'):
                self.desktop_page.update_dashboard()
            self.content_area.content = self.desktop_page
        elif route in ["PixelPilot", "PixelPilot "]: 
            self.content_area.content = ft.Text("Mouse setting loading", size=20)
        elif route == "Camera":
            self.content_area.content = self.camera_page
        elif route in ["CursorControl", "Cursor Control"]:
            self.content_area.content = self.cursor_control_page
        elif route in ["MouseBindings", "Mouse Bindings"]:
            if hasattr(self, 'camera_page') and hasattr(self.camera_page, 'executor'):
                current_mode = self.camera_page.executor.get_current_mode_name()
                if hasattr(self, 'mouse_bindings_page'):
                    self.mouse_bindings_page.update_active_mode_text(current_mode)
            self.content_area.content = self.mouse_bindings_page
        elif route in ["Apps", "Apps Page"]: 
            self.content_area.content = self.apps_page
        elif route in ["FaceGesture", "Face Gesture"]:
            self.content_area.content = self.gesture_determine_page
        elif route in ["Templates", "Templates ", "Template", "Şablonlar", "Settings"]:
            self.content_area.content = self.template_page
        else:
            self.content_area.content = ft.Text(f"{route} Ekranı", size=20)

        self.page.update()


def monitor_system_usage(duration_seconds=60):
    process = psutil.Process()
    logical_cores = psutil.cpu_count(logical=True)
    
    cpu_records = []
    ram_records = []
    time_axis = list(range(duration_seconds))
    
    print(f"\n[System] Hardware detected: {logical_cores} logical threads.")
    print(f"[System] Starting {duration_seconds}-second benchmark. Move your head and switch apps!")
    
    for _ in range(duration_seconds):
        raw_cpu = process.cpu_percent(interval=1.0)
        normalized_cpu = raw_cpu / logical_cores
        cpu_records.append(normalized_cpu)
        
        ram_mb = process.memory_info().rss / (1024 * 1024)
        ram_records.append(ram_mb)

    avg_cpu = sum(cpu_records) / len(cpu_records)
    peak_ram = max(ram_records)
    
    print("\n--- BENCHMARK RESULTS FOR ABSTRACT ---")
    print(f"Average CPU Utilization: {avg_cpu:.1f}%")
    print(f"Peak Memory (RAM) Footprint: {peak_ram:.1f} MB")
    print("--------------------------------------\n")
    
    plt.figure(figsize=(8, 5))
    
    plt.subplot(2, 1, 1)
    plt.plot(time_axis, cpu_records, color='#1f77b4', linewidth=2, label='CPU Usage')
    plt.ylabel('CPU Usage (%)', fontweight='bold')
    max_y = max(100, max(cpu_records) + 10)
    plt.ylim(0, max_y)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper right')
    
    plt.subplot(2, 1, 2)
    plt.plot(time_axis, ram_records, color='#d62728', linewidth=2, label='RAM Footprint')
    plt.xlabel('Time (Seconds)', fontweight='bold')
    plt.ylabel('Memory (MB)', fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig('system_performance.pdf', format='pdf', dpi=300)
    print("[Graph] Saved successfully as 'system_performance.pdf'")


def main(page: ft.Page):
    app = SensePilotApp(page)
    threading.Thread(target=monitor_system_usage, args=(60,), daemon=True).start()


if __name__ == "__main__":
    ft.run(main)