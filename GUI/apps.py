import os
import sys
import flet as ft
import tkinter as tk
from tkinter import filedialog

# =============================================================================
# SÜRÜMDEN BAĞIMSIZ GÜVENLİ KENARLIK (BORDER)
# =============================================================================
def get_border(width: int = 1, color: str = "#CCCCCC"):
    try:
        import flet_core.border as f_border
        return f_border.all(width, color)
    except Exception:
        pass
    try:
        side = ft.border.BorderSide(width, color)
        return ft.border.Border(top=side, right=side, bottom=side, left=side)
    except Exception:
        pass
    try:
        side = ft.BorderSide(width, color)
        return ft.Border(top=side, right=side, bottom=side, left=side)
    except Exception:
        return None


class AppsPage(ft.Column):
    def __init__(self, page=None, current_theme=None):
        super().__init__()
        self.expand = True
        self.spacing = 20
        
        # Tema Yedeği
        self.current_theme = current_theme if current_theme else {
            "bg": "#F8FAFC", "surface": "#FFFFFF", "primary": "#2563EB", 
            "text": "#0F172A", "text_secondary": "#64748B", "border": "#E2E8F0"
        }

        # EXE ve Asset yollarını bulma
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # Durumu Korunan Değişkenler (Tema değişse bile silinmez)
        self.custom_apps = []      
        self.current_view = "main" 
        self.selected_app_name = ""
        
        self.status_text = ft.Text("", size=16)
        self.path_input = ft.TextField(label="Dosya Yolu (Path)", width=400)
        
        self.build_ui()

    def apply_theme(self, new_theme):
        """Tema değiştiğinde main.py tarafından tetiklenir."""
        self.current_theme = new_theme
        self.build_ui()
        try:
            self.update()
        except Exception:
            pass

    def build_ui(self):
        """Arayüzü aktif temanın renkleriyle baştan inşa eder."""
        theme = self.current_theme
        
        # FLET'İN ESKİ RENKLİ BUTONLARI HAFIZADA TUTMASINI ENEGELLEYEN KESİN ÇÖZÜM
        self.controls.clear()
        
        title = ft.Text("Uygulama Başlatıcı", size=30, weight="bold", color=theme["text"])
        self.status_text.color = theme["text_secondary"]

        def open_app(app_command, app_name):
            try:
                os.startfile(app_command)
                self.status_text.value = f"{app_name} açıldı!"
                self.status_text.color = ft.Colors.GREEN
            except Exception as ex:
                self.status_text.value = f"Hata oluştu: {ex}"
                self.status_text.color = ft.Colors.RED
            self.update()

        def create_square_button(label_text, command, app_name, image_path=None):
            visual = ft.Image(src=image_path, width=60, height=60, fit="contain") if image_path else ft.Text(label_text[:3].upper(), size=30, weight="bold", color=theme["primary"])
            return ft.Container(
                content=ft.Column([visual, ft.Text(label_text, size=14, text_align="center", weight="bold", color=theme["text"])], alignment="center", horizontal_alignment="center", spacing=10),
                width=150, height=150, 
                bgcolor=theme["surface"],
                border_radius=15, ink=True,
                border=get_border(1, theme["border"]),
                on_click=lambda e: open_app(command, app_name),
            )

        def create_catalog_button(app_name):
            return ft.Container(
                # Yazı rengi sabit beyaz yerine temanın zıt (bg) rengine atandı.
                content=ft.Column([ft.Text(app_name[:2].upper(), size=45, color=theme["bg"], weight="bold"), ft.Text(app_name, size=14, text_align="center", weight="bold", color=theme["bg"])], alignment="center", horizontal_alignment="center", spacing=10),
                width=150, height=150, bgcolor=theme["primary"], border_radius=15, ink=True,
                on_click=lambda e: open_path_form(app_name),
            )

        def create_action_button(text, bg_color, text_color, action, width=120):
            return ft.Container(
                content=ft.Row([ft.Text(text, color=text_color, weight="bold")], alignment="center"),
                bgcolor=bg_color, width=width, height=50, border_radius=5, ink=True, on_click=action,
                border=get_border(1, theme["border"]) if bg_color == theme["surface"] else None
            )

        def get_img(filename):
            return os.path.join(self.base_dir, "assetts", filename)

        # ==========================================
        # View 1: Main Grid
        # ==========================================
        apps_controls = [
            create_square_button("Notebook", "notepad.exe", "Notebook", get_img("notepad.png")),
            create_square_button("Calculator", "calc.exe", "Calculator", get_img("calculator.png")),
            create_square_button("Screen Keyboard", "osk.exe", "Screen Keyboard", get_img("keyboard.png")),
            create_square_button("Calendar", "outlookcal:", "Calendar", get_img("calendar.png")),
            create_square_button("Paint", "mspaint.exe", "Paint", get_img("paint.png")),
            create_square_button("Files", "explorer.exe", "File Explorer", get_img("explorer.png")),
            create_square_button("Task Manager", "taskmgr.exe", "Task Manager", get_img("taskmgr.png"))
        ]

        for custom in self.custom_apps:
            apps_controls.append(create_square_button(custom["label"], custom["command"], custom["name"]))

        def show_catalog(e):
            self.current_view = "catalog"
            self.main_grid.visible = False
            self.path_form.visible = False
            self.catalog_grid.visible = True
            self.update()

        add_btn = ft.Container(
            content=ft.Column([ft.Text("+", size=60, color=theme["text"], weight="bold"), ft.Text("Yeni Ekle", size=14, text_align="center", weight="bold", color=theme["text"])], alignment="center", horizontal_alignment="center", spacing=10),
            width=150, height=150, 
            bgcolor=theme["surface"],
            border_radius=15, ink=True, on_click=show_catalog,
            border=get_border(1, theme["border"])
        )
        apps_controls.append(add_btn)

        self.main_grid = ft.Row(
            controls=apps_controls,
            wrap=True, spacing=20, run_spacing=20,
            visible=(self.current_view == "main")
        )

        # ==========================================
        # View 2: App Catalog Grid 
        # ==========================================
        def return_to_main(e):
            self.current_view = "main"
            self.catalog_grid.visible = False
            self.path_form.visible = False
            self.main_grid.visible = True
            self.update()

        back_btn = ft.Container(
            content=ft.Column([ft.Text("<", size=60, color=theme["text"], weight="bold"), ft.Text("Geri (Back)", size=14, text_align="center", weight="bold", color=theme["text"])], alignment="center", horizontal_alignment="center", spacing=10),
            width=150, height=150, 
            bgcolor=theme["surface"], 
            border_radius=15, ink=True, on_click=return_to_main,
            border=get_border(1, theme["border"])
        )

        self.catalog_grid = ft.Row(
            controls=[back_btn, create_catalog_button("Google Chrome"), create_catalog_button("Steam"), create_catalog_button("Spotify"), create_catalog_button("Klasör (Folder)"), create_catalog_button("Özel (Custom)")],
            wrap=True, spacing=20, run_spacing=20, 
            visible=(self.current_view == "catalog") 
        )

        # ==========================================
        # View 3: Path Input Form
        # ==========================================
        self.form_title = ft.Text(f"{self.selected_app_name} Yolu Ekle (Add Path)", size=20, weight="bold", color=theme["primary"])
        self.path_input.color = theme["text"]
        self.path_input.border_color = theme["border"]

        def open_path_form(app_name):
            self.selected_app_name = app_name
            self.form_title.value = f"{app_name} Yolu Ekle (Add Path)"
            self.path_input.value = ""
            self.current_view = "form"
            self.catalog_grid.visible = False
            self.path_form.visible = True
            self.update()

        def browse_for_exe(e):
            root = tk.Tk()
            root.attributes("-topmost", True)
            root.withdraw()
            file_path = filedialog.askopenfilename(title="Uygulama Seç (.exe) / Select App", filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")])
            root.destroy()
            if file_path:
                self.path_input.value = file_path.replace("/", "\\")
                self.update()

        def browse_for_folder(e):
            root = tk.Tk()
            root.attributes("-topmost", True)
            root.withdraw()
            folder_path = filedialog.askdirectory(title="Klasör Seç / Open Folder")
            root.destroy()
            if folder_path:
                self.path_input.value = folder_path.replace("/", "\\")
                self.update()

        def save_new_app(e):
            path = self.path_input.value
            name = self.selected_app_name
            if path:
                self.custom_apps.append({"label": name, "command": path, "name": name})
                new_app_btn = create_square_button(label_text=name, command=path, app_name=name)
                self.main_grid.controls.insert(-1, new_app_btn)
                return_to_main(e)

        browse_exe_btn = create_action_button(".exe Seç", theme["surface"], theme["text"], browse_for_exe, 100)
        browse_folder_btn = create_action_button("Klasör Seç", theme["primary"], theme["bg"], browse_for_folder, 100)

        self.path_form = ft.Container(
            visible=(self.current_view == "form"), bgcolor=theme["surface"], padding=30, border_radius=10,
            border=get_border(1, theme["border"]),
            content=ft.Column([
                self.form_title,
                ft.Text("Bilgisayarınızdan uygulama (.exe) veya klasör seçin:", size=14, color=theme["text_secondary"]),
                ft.Row([self.path_input, browse_exe_btn, browse_folder_btn], wrap=True), 
                ft.Container(height=20),
                ft.Row([
                    create_action_button("İptal (Cancel)", theme["surface"], theme["text"], return_to_main, 150), 
                    create_action_button("Kaydet (Save)", theme["primary"], theme["bg"], save_new_app, 150)
                ])
            ])
        )

        self.controls.extend([title, ft.Divider(color=theme["border"]), self.main_grid, self.catalog_grid, self.path_form, ft.Container(height=20), self.status_text])