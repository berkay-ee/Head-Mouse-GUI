import os
import sys
import flet as ft
import tkinter as tk
from tkinter import filedialog

class AppsPage(ft.Column):
    def __init__(self, page=None):
        super().__init__()
        self.expand = True
        self.spacing = 20

        title = ft.Text("Uygulama Başlatıcı", size=30, weight="bold")
        self.status_text = ft.Text("", size=16)

        def open_app(app_command, app_name):
            try:
                os.startfile(app_command)
                self.status_text.value = f"{app_name} açıldı!"
                self.status_text.color = "green"
            except Exception as ex:
                self.status_text.value = f"Hata oluştu: {ex}"
                self.status_text.color = "red"
            self.update()

        def create_square_button(label_text, command, app_name, image_path=None):
            visual = ft.Image(src=image_path, width=60, height=60, fit="contain") if image_path else ft.Text(label_text[:3].upper(), size=30, weight="bold", color="blue")
            return ft.Container(
                content=ft.Column([visual, ft.Text(label_text, size=14, text_align="center", weight="bold")], alignment="center", horizontal_alignment="center", spacing=10),
                width=150, height=150, bgcolor="#e0e0e0", border_radius=15, ink=True,
                on_click=lambda e: open_app(command, app_name),
            )

        def create_catalog_button(app_name):
            return ft.Container(
                content=ft.Column([ft.Text(app_name[:2].upper(), size=45, color="white", weight="bold"), ft.Text(app_name, size=14, text_align="center", weight="bold", color="white")], alignment="center", horizontal_alignment="center", spacing=10),
                width=150, height=150, bgcolor="#1976d2", border_radius=15, ink=True,
                on_click=lambda e: open_path_form(app_name),
            )

        def create_action_button(text, bg_color, text_color, action, width=120):
            return ft.Container(
                content=ft.Row([ft.Text(text, color=text_color, weight="bold")], alignment="center"),
                bgcolor=bg_color, width=width, height=50, border_radius=5, ink=True, on_click=action
            )

        # ==========================================
        # View 1: Main Grid (DYNAMIC PATHS ADDED HERE)
        # ==========================================
        # This code finds exactly where the .exe is running on ANY computer
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        def get_img(filename):
            return os.path.join(base_dir, "assetts", filename)

        notepad_btn = create_square_button("Notebook", "notepad.exe", "Notebook", get_img("notepad.png"))
        calc_btn = create_square_button("Calculator", "calc.exe", "Calculator", get_img("calculator.png"))
        keyboard_btn = create_square_button("Screen Keyboard", "osk.exe", "Screen Keyboard", get_img("keyboard.png"))
        calendar_btn = create_square_button("Calendar", "outlookcal:", "Calendar", get_img("calendar.png"))
        paint_btn = create_square_button("Paint", "mspaint.exe", "Paint", get_img("paint.png"))
        explorer_btn = create_square_button("Files", "explorer.exe", "File Explorer", get_img("explorer.png"))
        taskmgr_btn = create_square_button("Task Manager", "taskmgr.exe", "Task Manager", get_img("taskmgr.png"))

        self.main_grid = ft.Row(
            controls=[notepad_btn, calc_btn, keyboard_btn, calendar_btn, paint_btn, explorer_btn, taskmgr_btn],
            wrap=True, spacing=20, run_spacing=20,
        )

        def show_catalog(e):
            self.main_grid.visible = False
            self.path_form.visible = False
            self.catalog_grid.visible = True
            self.update()

        add_btn = ft.Container(
            content=ft.Column([ft.Text("+", size=60, color="black", weight="bold"), ft.Text("Yeni Ekle", size=14, text_align="center", weight="bold", color="black")], alignment="center", horizontal_alignment="center", spacing=10),
            width=150, height=150, bgcolor="#cccccc", border_radius=15, ink=True, on_click=show_catalog,
        )
        self.main_grid.controls.append(add_btn)

        # ==========================================
        # View 2: App Catalog Grid 
        # ==========================================
        def return_to_main(e):
            self.catalog_grid.visible = False
            self.path_form.visible = False
            self.main_grid.visible = True
            self.update()

        back_btn = ft.Container(
            content=ft.Column([ft.Text("<", size=60, color="black", weight="bold"), ft.Text("Geri (Back)", size=14, text_align="center", weight="bold", color="black")], alignment="center", horizontal_alignment="center", spacing=10),
            width=150, height=150, bgcolor="#cccccc", border_radius=15, ink=True, on_click=return_to_main,
        )

        self.catalog_grid = ft.Row(
            controls=[back_btn, create_catalog_button("Google Chrome"), create_catalog_button("Steam"), create_catalog_button("Spotify"), create_catalog_button("Klasör (Folder)"), create_catalog_button("Özel (Custom)")],
            wrap=True, spacing=20, run_spacing=20, visible=False 
        )

        # ==========================================
        # View 3: Path Input Form
        # ==========================================
        self.selected_app_name = ""
        self.path_input = ft.TextField(label="Dosya Yolu (Path)", width=400)
        self.form_title = ft.Text("", size=20, weight="bold", color="blue")

        def open_path_form(app_name):
            self.selected_app_name = app_name
            self.form_title.value = f"{app_name} Yolu Ekle (Add Path)"
            self.path_input.value = ""
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
                new_app_btn = create_square_button(label_text=name, command=path, app_name=name)
                self.main_grid.controls.insert(-1, new_app_btn)
                return_to_main(e)

        browse_exe_btn = create_action_button(".exe Seç", "grey", "white", browse_for_exe, 100)
        browse_folder_btn = create_action_button("Klasör Seç", "#ff9800", "white", browse_for_folder, 100)

        self.path_form = ft.Container(
            visible=False, bgcolor="#f5f5f5", padding=30, border_radius=10,
            content=ft.Column([
                self.form_title,
                ft.Text("Bilgisayarınızdan uygulama (.exe) veya klasör seçin:", size=14),
                ft.Row([self.path_input, browse_exe_btn, browse_folder_btn], wrap=True), 
                ft.Container(height=20),
                ft.Row([create_action_button("İptal (Cancel)", "#cccccc", "black", show_catalog, 150), create_action_button("Kaydet (Save)", "#1976d2", "white", save_new_app, 150)])
            ])
        )

        self.controls = [title, ft.Divider(), self.main_grid, self.catalog_grid, self.path_form, ft.Container(height=20), self.status_text]