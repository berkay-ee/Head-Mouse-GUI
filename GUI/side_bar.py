import flet as ft

class Sidebar(ft.Container):
    def __init__(self, on_menu_click, current_theme):
        super().__init__()
        self.on_menu_click = on_menu_click 
        self.current_theme = current_theme
        
        self.width = 250
        self.padding = 20
        self.bgcolor = self.current_theme["surface"]
        self.content = self.build_menu()

    def nav_item(self, text, icon, route_name):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=20, color=self.current_theme["text_secondary"]),
                ft.Text(text, size=14, color=self.current_theme["text"])
            ], spacing=12),
            padding=12,
            border_radius=8,
            ink=True,
            on_click=lambda e: self.on_menu_click(route_name) 
        )

    def build_menu(self):
        return ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.NAVIGATION, color=self.current_theme["primary"], size=24),
                ft.Text("PixelPilot", size=16, weight=ft.FontWeight.BOLD, color=self.current_theme["text"])
            ], spacing=10),
            ft.Divider(height=20, color=self.current_theme["border"]),
            
            ft.Text("MENÜ", size=10, weight=ft.FontWeight.BOLD, color=self.current_theme["text_secondary"]),
            self.nav_item("Desktop", ft.Icons.DESKTOP_MAC, "Desktop"),
            self.nav_item("Camera", ft.Icons.CAMERA_ALT, "Camera"),
            self.nav_item("Cursor Control", ft.Icons.NEAR_ME, "Cursor Control"),
            self.nav_item("Mouse Bindings", ft.Icons.MOUSE, "Mouse Bindings"),
            self.nav_item("Apps", ft.Icons.GRID_VIEW, "Apps"),
            self.nav_item("Face Gesture", ft.Icons.FACE, "Face Gesture"),
            self.nav_item("Templates", ft.Icons.PALETTE, "Templates"),
        ], spacing=5)