import flet as ft
from typing import Callable, Optional

# =============================================================================
# 0. SÜRÜMDEN BAĞIMSIZ GÜVENLİ BİLEŞENLER
# =============================================================================
def create_border(width: int = 1, color: str = "#CCCCCC"):
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

def build_outlined_button(text: str, icon: str, fg_color: str):
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(icon, size=16, color=fg_color),
                ft.Text(text, size=13, weight=ft.FontWeight.BOLD, color=fg_color),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        border=create_border(1, fg_color),
        height=42,          
        border_radius=8,
    )

# =============================================================================
# 1. RENK PALETLERİ
# =============================================================================
COLOR_TEMPLATES = {
    "light": {
        "id": "light",
        "name": "Standart Mod",
        "description": "Bright and balanced colors for everyday use. Offers a standard brightness that is easy on the eyes.",
        "bg": "#F8FAFC",
        "surface": "#FFFFFF",
        "primary": "#2563EB",
        "text": "#0F172A",
        "text_secondary": "#64748B",
        "border": "#E2E8F0",
        "theme_mode": ft.ThemeMode.LIGHT,
    },
    "night": {
        "id": "night",
        "name": "Night Mode (Dark)",
        "description": "Deep navy and black tones prevent glare in low light. Reduces eye strain.",
        "bg": "#0B0F19",
        "surface": "#1E293B",
        "primary": "#38BDF8",
        "text": "#F8FAFC",
        "text_secondary": "#94A3B8",
        "border": "#334155",
        "theme_mode": ft.ThemeMode.DARK,
    },
    "reading": {
        "id": "reading",
        "name": "Reading Mode",
        "description": "Warm cream and coffee tones that block blue light soothe the eyes with prolonged use.",
        "bg": "#F5EFE6",
        "surface": "#E8DFCA",
        "primary": "#8D6E63",
        "text": "#3E2723",
        "text_secondary": "#5D4037",
        "border": "#D7CCC8",
        "theme_mode": ft.ThemeMode.LIGHT,
    },
    "comfort": {
        "id": "comfort",
        "name": "Eye Comfort Mode",
        "description": "It features soft, matte slate grey and sage green accents. High contrast prevents glare.",
        "bg": "#22272E",
        "surface": "#2D333B",
        "primary": "#7EE787",
        "text": "#ADBAC7",
        "text_secondary": "#768390",
        "border": "#444C56",
        "theme_mode": ft.ThemeMode.DARK,
    },
    "colorblind": {
        "id": "colorblind",
        "name": "Color Blind Mode",
        "description": "Red colorblind-friendly palette with high contrast.",
        "bg": "#000000",
        "surface": "#1A1A1A",
        "primary": "#FFC107",
        "text": "#FFFFFF",
        "text_secondary": "#64B5F6",
        "border": "#FFFFFF",
        "theme_mode": ft.ThemeMode.DARK,
    },
}

# =============================================================================
# 2. BAŞ FARE KULLANIM ŞABLONLARI
# =============================================================================
USAGE_PRESETS = {
    "precision": {
        "name": "Hassas Çizim & Tasarım",
        "description": "Yüksek titreşim filtresi, düşük imleç hızı. Mikrometre seviyesinde tıklamalar için.",
        "speed": 2,
        "smoothing": 0.85,
        "icon": "brush",
    },
    "general": {
        "name": "Standart Ofis & Gezinme",
        "description": "Dengeli imleç hızı ve standart tıklama eşiği. Günlük Windows/Mac kullanımı içindir.",
        "speed": 5,
        "smoothing": 0.60,
        "icon": "desktop_mac",
    },
    "fast": {
        "name": "Hızlı Gezinme & Tepki",
        "description": "Geniş kafa hareketleri için yüksek hız, minimum gecikme. Oyunlar ve hızlı geçişler için.",
        "speed": 8,
        "smoothing": 0.25,
        "icon": "speed",
    },
}

# =============================================================================
# 3. ŞABLON VE TEMA SEÇİM SAYFASI
# =============================================================================
class TemplatePage(ft.Container):
    def __init__(
        self,
        on_theme_select: Optional[Callable[[dict], None]] = None,
        on_preset_select: Optional[Callable[[dict], None]] = None,
        current_theme_key: str = "light",
    ):
        super().__init__(expand=True, padding=20)
        self.on_theme_select = on_theme_select
        self.on_preset_select = on_preset_select
        self.current_theme = COLOR_TEMPLATES.get(current_theme_key, COLOR_TEMPLATES["light"])

        self.content = ft.ListView(
            expand=True,
            spacing=20,
            controls=[
                ft.Text("Color Templates", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Choose the color theme that best fits your workspace and visual sensitivity:", size=14),
                self._build_theme_cards(),
                ft.Divider(height=30, color="transparent"),
                ft.Text("Primary Mouse Sensitivity Profiles", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Pre-designed cursor and filtering templates for different scenarios:", size=14),
                self._build_preset_cards(),
            ],
        )

    def _build_theme_cards(self) -> ft.ResponsiveRow:
        cards = []
        for key, t in COLOR_TEMPLATES.items():
            is_active = key == self.current_theme["id"]
            border_color = t["primary"] if is_active else t["border"]

            palette_strip = ft.Container(
                height=35,
                border_radius=8,
                border=create_border(1, t["border"]),
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                content=ft.Row(
                    [
                        ft.Container(expand=1, bgcolor=t["primary"], tooltip="Ana Renk"),
                        ft.Container(expand=1, bgcolor=t["bg"], tooltip="Arka Plan Rengi"),
                        ft.Container(expand=1, bgcolor=t["surface"], tooltip="Kart Rengi"),
                        ft.Container(expand=1, bgcolor=t["text"], tooltip="Yazı Rengi"),
                    ],
                    spacing=0,
                )
            )

            card = ft.Container(
                height=220,
                padding=20,
                border_radius=12,
                bgcolor=t["surface"],
                border=create_border(2, border_color),
                on_click=lambda e, k=key: self._handle_theme_change(k),
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                # Flet'i çökerten Icon kaldırıldı, yerine seçimi belirten Radio Button (yuvarlak) eklendi
                                ft.Container(
                                    width=18, height=18, border_radius=9,
                                    bgcolor=t["primary"] if is_active else "transparent",
                                    border=create_border(2, t["primary"])
                                ),
                                ft.Text(t["name"], weight=ft.FontWeight.BOLD, size=15, color=t["text"]),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=10,
                        ),
                        ft.Text(t["description"], size=13, color=t["text_secondary"]),
                        ft.Container(expand=True),
                        palette_strip,
                    ],
                    spacing=12,
                ),
                col={"sm": 12, "md": 6, "lg": 4},
            )
            cards.append(card)
        return ft.ResponsiveRow(controls=cards, spacing=15)

    def _build_preset_cards(self) -> ft.ResponsiveRow:
        cards = []
        for key, p in USAGE_PRESETS.items():
            card = ft.Container(
                height=230,
                padding=20,
                border_radius=12,
                bgcolor=self.current_theme["surface"],
                border=create_border(2, self.current_theme["border"]),
                on_click=lambda e, preset=p: self._handle_preset_change(preset),
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Icon(p["icon"], size=22, color=self.current_theme["text"]), 
                            ft.Text(p["name"], weight=ft.FontWeight.BOLD, size=16, color=self.current_theme["text"])
                        ]),
                        ft.Text(p["description"], size=13, color=self.current_theme["text_secondary"]),
                        ft.Text(f"Hız Çarpanı: {p['speed']}x\nFiltreleme: %{int(p['smoothing']*100)}", size=12, weight=ft.FontWeight.BOLD, color=self.current_theme["primary"]),
                        ft.Container(expand=True),
                        build_outlined_button(
                            text="Şablonu Yükle",
                            icon="bolt",
                            fg_color=self.current_theme["text"]
                        ),
                    ],
                    spacing=12,
                ),
                col={"sm": 12, "md": 4},
            )
            cards.append(card)
        return ft.ResponsiveRow(controls=cards, spacing=15)

    def _handle_theme_change(self, theme_key: str):
        self.current_theme = COLOR_TEMPLATES[theme_key]
        
        # SİHİRLİ DOKUNUŞ: Tıklandığında kartları kendi içimizde güvenle baştan oluşturuyoruz. 
        # Bu Flet'in çökmesini %100 engeller.
        self.content.controls[2] = self._build_theme_cards()
        self.content.controls[6] = self._build_preset_cards()
        self.update()

        # Sonra ana sisteme bildiriyoruz
        if self.on_theme_select:
            self.on_theme_select(self.current_theme)

    def _handle_preset_change(self, preset: dict):
        if self.on_preset_select:
            self.on_preset_select(preset)