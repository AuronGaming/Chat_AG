"""Конфигурация темы Chat_AG"""

COLORS = {
    'bg_main': '#0f0f14',
    'bg_secondary': '#1a1a23',
    'bg_input': '#2a2a35',
    'bg_hover': '#3a3a45',
    'border': '#3a3a45',
    'text_primary': '#ffffff',
    'text_secondary': '#a0a0a0',
    'accent': '#2ea043',
    'error': '#ff4444',
    'warning': '#ffaa00',
    'success': '#2ea043',
}

BUTTON_DEFAULT = f"""
    QPushButton {{
        background-color: {COLORS['bg_input']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 6px 16px;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['bg_hover']};
    }}
"""

BUTTON_ACCENT = f"""
    QPushButton {{
        background-color: {COLORS['accent']};
        color: white;
        border: none;
        border-radius: 4px;
        padding: 6px 16px;
        font-size: 13px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: #238636;
    }}
"""

INPUT_STYLE = f"""
    QLineEdit {{
        background-color: {COLORS['bg_input']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 6px 10px;
        font-size: 13px;
    }}
    QLineEdit:focus {{
        border-color: {COLORS['accent']};
    }}
"""

LIST_STYLE = f"""
    QListWidget {{
        background-color: {COLORS['bg_main']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        font-size: 13px;
    }}
    QListWidget::item {{
        padding: 8px 12px;
        border-bottom: 1px solid {COLORS['border']};
    }}
    QListWidget::item:selected {{
        background-color: {COLORS['accent']};
        color: white;
    }}
    QListWidget::item:hover {{
        background-color: {COLORS['bg_hover']};
    }}
"""