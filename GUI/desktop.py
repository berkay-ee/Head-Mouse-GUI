import flet as ft
import asyncio
import threading
from bleak import BleakScanner, BleakClient
import pyautogui

# ESP32 connected device name and characteristic UUID
DEVICE_NAME = "PixelPilot"
SENSOR_CHARACTERISTIC_UUID = "19b10001-e8f2-537e-4f6c-d104766a1214"
pyautogui.PAUSE = 0

class DesktopPage(ft.Container):
    def __init__(self, mouse_controller, dwell_clicker, camera_page=None, on_ble_connected_callback=None, current_theme=None):
        super().__init__()
        self.expand = True
        self.padding = 30
        self.bgcolor = ft.Colors.TRANSPARENT
        
        self.mouse_controller = mouse_controller
        self.dwell_clicker = dwell_clicker
        self.camera_page = camera_page
        self.on_ble_connected = on_ble_connected_callback
        
        # Eğer main.py'den tema gelmezse diye güvenlik yedeği (Fallback)
        self.current_theme = current_theme if current_theme else {
            "bg": "#F8FAFC", "surface": "#FFFFFF", "primary": "#2563EB", 
            "text": "#0F172A", "text_secondary": "#64748B", "border": "#E2E8F0"
        }
        
        self.ble_client = None  
        self.ble_loop = None    

        # ==========================================
        # DURUMU (STATE) KORUNACAK SABİT BİLEŞENLER
        # ==========================================
        # Tema değişse bile Bluetooth durum yazısı ve ayar değerleri kaybolmamalı!
        self.status_text = ft.Text("Connection Pending...", size=14, color=ft.Colors.RED_700)
        self.connect_btn = ft.Button(
            content="Connect to HeadMouse", icon=ft.Icons.BLUETOOTH, 
            bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, on_click=self.connect_ble_click
        )
        
        self.val_hor_speed = ft.Text("-", size=13)
        self.val_ver_speed = ft.Text("-", size=13)
        self.val_dwell_status = ft.Text("-", size=13)
        self.val_dwell_time = ft.Text("-", size=13)

        # İlk arayüz çizimi
        self.build_ui()

    def apply_theme(self, new_theme):
        """Tema değiştiğinde main.py tarafından tetiklenir."""
        self.current_theme = new_theme
        self.build_ui() # Arayüzü yeni renklerle baştan oluştur
        self.update()   # Sayfayı yenile

    def build_ui(self):
        """Arayüzü aktif temanın renkleriyle inşa eder."""
        theme = self.current_theme

        # Kenarlık renklerini aktif temadan al
        card_border = ft.Border(
            top=ft.BorderSide(1, theme["border"]), right=ft.BorderSide(1, theme["border"]),
            bottom=ft.BorderSide(1, theme["border"]), left=ft.BorderSide(1, theme["border"])
        )

        info_border = ft.Border(
            top=ft.BorderSide(1, theme["primary"]), right=ft.BorderSide(1, theme["primary"]),
            bottom=ft.BorderSide(1, theme["primary"]), left=ft.BorderSide(1, theme["primary"])
        )

        header = ft.Column([
            ft.Text("Desktop Profile", size=28, weight=ft.FontWeight.BOLD, color=theme["text"]),
        ], spacing=5)
        
        status_card = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.BLUETOOTH_CONNECTED, color=theme["primary"], size=40),
                ft.Column([
                    ft.Text("Device Status", weight=ft.FontWeight.BOLD, size=16, color=theme["text"]),
                    self.status_text, self.connect_btn # Durumu korunan nesneler!
                ], spacing=4)
            ]),
            padding=20, bgcolor=theme["surface"], border_radius=12, border=card_border,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.BLACK_12), width=450
        )

        # Metin renklerini temaya uygun hale getir
        self.val_hor_speed.color = theme["text_secondary"]
        self.val_ver_speed.color = theme["text_secondary"]
        self.val_dwell_time.color = theme["text_secondary"]
        # NOT: val_dwell_status'un rengi (Yeşil/Kırmızı) update_dashboard içinde belirleniyor, buraya yazmıyoruz.

        def summary_item(icon, title, value_control):
            return ft.Container(
                content=ft.Row([
                    # İkon kutusu arka planını uygulamanın ana rengine uyumlu yaptık
                    ft.Container(content=ft.Icon(icon, color=theme["primary"], size=24), padding=10, bgcolor=theme["bg"], border_radius=8),
                    ft.Column([ft.Text(title, weight=ft.FontWeight.BOLD, size=14, color=theme["text"]), value_control], spacing=2)
                ]),
                padding=15, bgcolor=theme["surface"], border_radius=12, border=card_border, expand=True
            )

        summary_row = ft.Row([
            summary_item(ft.Icons.SPEED, "Hor. Sensitivity", self.val_hor_speed),
            summary_item(ft.Icons.SWAP_VERT, "Ver. Sensitivity", self.val_ver_speed),
            summary_item(ft.Icons.MOUSE, "Auto Click", self.val_dwell_status),
            summary_item(ft.Icons.TIMER, "Dwell Time", self.val_dwell_time),
        ], spacing=20)

        info_box = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE, color=theme["primary"]),
                ft.Text("To change settings, use the 'Cursor Control' or 'Mouse Bindings' tabs in the left menu.", color=theme["text_secondary"], size=13)
            ]),
            padding=15, bgcolor=theme["surface"], border_radius=10, border=info_border
        )

        # Temaya göre inşa edilmiş sütunu ana Container'ın content'ine atıyoruz
        self.content = ft.Column([
            header, 
            ft.Divider(height=25, color=ft.Colors.TRANSPARENT),
            status_card, 
            ft.Divider(height=25, color=ft.Colors.TRANSPARENT),
            ft.Text("Active Profile Summary", size=18, weight=ft.FontWeight.BOLD, color=theme["text"]),
            summary_row, 
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            info_box
        ], horizontal_alignment=ft.CrossAxisAlignment.START, scroll=ft.ScrollMode.AUTO)

        self.update_dashboard()

    # ==========================================
    # LIVE DATA UPDATER (Kept safely empty so camera doesn't crash)
    # ==========================================
    def update_live_data(self, pitch, yaw, mode, method, is_scroll):
        """Silently ignores camera data so the UI remains clean."""
        pass

    # ==========================================
    # STATIC DASHBOARD UPDATER
    # ==========================================
    def update_dashboard(self):
        if hasattr(self, 'mouse_controller') and self.mouse_controller:
            level_x = int(self.mouse_controller.sensitivity_x / 10.0)
            level_y = int(self.mouse_controller.sensitivity_y / 10.0)
            self.val_hor_speed.value = f"Level {level_x} ({self.mouse_controller.sensitivity_x})"
            self.val_ver_speed.value = f"Level {level_y} ({self.mouse_controller.sensitivity_y})"
            
        if hasattr(self, 'dwell_clicker') and self.dwell_clicker:
            status = "ON (Active)" if self.dwell_clicker.enabled else "OFF (Inactive)"
            color = ft.Colors.GREEN_700 if self.dwell_clicker.enabled else ft.Colors.RED_700
            self.val_dwell_status.value = status
            self.val_dwell_status.color = color
            self.val_dwell_status.weight = ft.FontWeight.BOLD
            
            level_t = int(round(self.dwell_clicker.dwell_time / 0.15))
            self.val_dwell_time.value = f"Level {level_t} ({self.dwell_clicker.dwell_time:.2f} s)"
        
        try:
            self.update()
        except Exception:
            pass

    # ==========================================
    # BLUETOOTH (BLE) asynchronous connection
    # ==========================================
    def connect_ble_click(self, e):
        self.status_text.value = "Device Searching..."
        self.status_text.color = ft.Colors.ORANGE_700
        self.connect_btn.disabled = True
        self.update() 
        threading.Thread(target=self._run_isolated_ble_loop, daemon=True).start()

    def _run_isolated_ble_loop(self):
        self.ble_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.ble_loop)
        self.ble_loop.run_until_complete(self._ble_connection_task())

    async def _ble_connection_task(self):
        try:
            device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=5.0)
            if not device:
                self.status_text.value = "Error: HeadMouse not found!"
                self.status_text.color = ft.Colors.RED_700
                self.connect_btn.disabled = False
                self.update()
                return

            self.status_text.value = "Found! Connecting..."
            self.update()

            self.ble_client = BleakClient(device, disconnected_callback=self.handle_disconnect)
            await self.ble_client.connect()

            self.status_text.value = "Connected!"
            self.status_text.color = ft.Colors.GREEN_700
            self.connect_btn.content = "Connected"  
            self.update()

            if self.on_ble_connected:
                self.on_ble_connected()

            await self.ble_client.start_notify(SENSOR_CHARACTERISTIC_UUID, self.handle_rx)
            while self.ble_client.is_connected:
                await asyncio.sleep(1)

        except Exception as ex: 
            self.status_text.value = "Connection Error!"
            self.status_text.color = ft.Colors.RED_700
            self.connect_btn.disabled = False
            self.update()

    def stop_ble(self):
        if self.ble_client and self.ble_client.is_connected:
            try:
                asyncio.run_coroutine_threadsafe(self.ble_client.disconnect(), self.ble_loop)
            except Exception as e:
                pass
            
    def handle_disconnect(self, client):
        self.status_text.value = "Connection Lost!"
        self.status_text.color = ft.Colors.RED_700
        self.connect_btn.content = "Reconnect"
        self.connect_btn.disabled = False
        self.update()
        self.ble_client = None

    def handle_rx(self, sender, data):
        try:
            decoded_data = data.decode('utf-8')
            parts = decoded_data.split(',')
            x = int(parts[0].split(':')[1]) 
            y = int(parts[1].split(':')[1]) 
            b = int(parts[2].split(':')[1]) 
            pyautogui.move(x, y, _pause=False)
            if b == 1:
                pyautogui.click()
        except Exception as e:
            pass