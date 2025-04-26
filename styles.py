from tkinter import font as tkfont

class Styles:
    def __init__(self, root):
        self.root = root
        
        # Modern color scheme
        self.bg_dark = "#121218"
        self.bg_medium = "#1a1a24"
        self.bg_light = "#242432"
        self.bg_input = "#2a2a3a"
        self.accent = "#00b0ff"  # Sky blue
        self.accent_hover = "#0088cc"
        self.text_primary = "#ffffff"
        self.text_secondary = "#b0b0b0"
        self.danger = "#ff4444"
        
        # Crisp, modern fonts
        self.font_normal = tkfont.Font(root=root, family="Segoe UI", size=12)
        self.font_small = tkfont.Font(root=root, family="Segoe UI", size=10)
        self.font_bold = tkfont.Font(root=root, family="Segoe UI", size=12, weight="bold")
        self.font_large = tkfont.Font(root=root, family="Segoe UI", size=14)
        
        # Button styles
        self.button_style = {
            "bg": self.accent,
            "fg": self.text_primary,
            "borderwidth": 0,
            "highlightthickness": 0,
            "activebackground": self.accent_hover,
            "font": self.font_normal
        }
        
        self.secondary_button_style = {
            "bg": self.bg_light,
            "fg": self.text_primary,
            "borderwidth": 0,
            "highlightthickness": 0,
            "activebackground": self.bg_medium,
            "font": self.font_normal
        }
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            self.popup.bind_all("<MouseWheel>", _on_mousewheel)
