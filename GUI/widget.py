import flet as ft

class MiniHUD(ft.WindowDragArea):
    """
    Kamera uygulamasından bağımsız çalışan, her yere sürüklenebilen HUD Widget sınıfı.
    Tüm masaüstü (Desktop) bilgilerini kompakt bir şekilde gösterir.
    """
    def __init__(self, on_restore):
        self.on_restore = on_restore
        
        # Görüntü ve temel metinler
        self.hud_image = ft.Image(src="", width=160, height=110, fit="cover", border_radius=8, gapless_playback=True)
        self.hud_values = ft.Text("Başlatılıyor...", color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD)
        
        # Ana ekrana dönüş butonu
        self.restore_btn = ft.IconButton(
            ft.Icons.FULLSCREEN_EXIT, icon_size=18, icon_color=ft.Colors.WHITE, 
            on_click=self._handle_restore, tooltip="Ana Ekrana Dön", padding=0
        )
        
        # =======================================================
        # MASAÜSTÜ (DESKTOP) VERİLERİ İÇİN METİN ALANLARI
        # =======================================================
        self.ble_status = ft.Text("Bekleniyor...", size=11, weight="bold", color=ft.Colors.ORANGE_400)
        self.val_x = ft.Text("-", size=11, weight="bold", color=ft.Colors.WHITE)
        self.val_y = ft.Text("-", size=11, weight="bold", color=ft.Colors.WHITE)
        self.val_dwell = ft.Text("-", size=11, weight="bold", color=ft.Colors.WHITE)
        self.val_time = ft.Text("-", size=11, weight="bold", color=ft.Colors.WHITE)

        # Bilgi satırlarını standartlaştırmak için yardımcı fonksiyon
        def _info(icon, label, text_obj):
            return ft.Row([
                ft.Icon(icon, size=14, color=ft.Colors.CYAN_300),
                ft.Text(label, size=11, color=ft.Colors.WHITE_70),
                text_obj
            ], spacing=4)

        # Şık widget çerçevesi
        hud_container = ft.Container(
            bgcolor=ft.Colors.BLUE_GREY_900,
            border_radius=12,
            padding=10,
            border=ft.Border(
                top=ft.BorderSide(2, ft.Colors.CYAN_400), right=ft.BorderSide(2, ft.Colors.CYAN_400),
                bottom=ft.BorderSide(2, ft.Colors.CYAN_400), left=ft.BorderSide(2, ft.Colors.CYAN_400)
            ),
            content=ft.Column([
                self.hud_image,
                ft.Row([self.hud_values, self.restore_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(height=1, color=ft.Colors.CYAN_800),
                
                # 1. Satır: Bluetooth Durumu
                _info(ft.Icons.BLUETOOTH, "Cihaz:", self.ble_status),
                
                # 2. Satır: Profil Özeti (2 Sütun halinde)
                ft.Row([
                    ft.Column([
                        _info(ft.Icons.SPEED, "X Hız:", self.val_x),
                        _info(ft.Icons.SWAP_VERT, "Y Hız:", self.val_y),
                    ], spacing=4, expand=1),
                    ft.Column([
                        _info(ft.Icons.MOUSE, "Oto Tık:", self.val_dwell),
                        _info(ft.Icons.TIMER, "Süre:", self.val_time),
                    ], spacing=4, expand=1)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                
            ], spacing=8)
        )
        
        super().__init__(content=hud_container)

    def _handle_restore(self, e):
        """Kapatma tuşuna basıldığında ana sayfanın fonksiyonunu tetikler."""
        if self.on_restore:
            self.on_restore()

    def update_hud(self, base64_img, pitch, yaw, mode, ble_stat, x_val, y_val, dwell_stat, dwell_time_val):
        """Kamera ve masaüstü verilerini günceller"""
        self.hud_image.src = f"data:image/jpeg;base64,{base64_img}"
        self.hud_values.value = f"P: {int(pitch)} | Y: {int(yaw)} | Mod: {mode}"
        
        self.ble_status.value = ble_stat
        self.val_x.value = x_val
        self.val_y.value = y_val
        self.val_dwell.value = dwell_stat
        self.val_time.value = dwell_time_val
        
        # Duruma göre renkleri canlı olarak değiştir
        self.ble_status.color = ft.Colors.GREEN_400 if "Connected" in ble_stat else ft.Colors.ORANGE_400
        self.val_dwell.color = ft.Colors.GREEN_400 if "ON" in dwell_stat or "AÇIK" in dwell_stat else ft.Colors.RED_400

        try:
            self.hud_image.update()
            self.hud_values.update()
            self.ble_status.update()
            self.val_x.update()
            self.val_y.update()
            self.val_dwell.update()
            self.val_time.update()
        except Exception:
            pass