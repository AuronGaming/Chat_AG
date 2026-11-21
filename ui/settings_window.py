"""Окно настроек Chat_AG (Маршрутизатор)"""

from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout,
                             QListWidget, QListWidgetItem, QWidget,
                             QPushButton, QScrollArea, QSplitter, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from ui.theme_config import COLORS, BUTTON_DEFAULT, BUTTON_ACCENT, LIST_STYLE
from ui.custom_title_bar import CustomTitleBar
from ui.settings import TTSSection, DonateTTSSection, EventSoundsSection, ConnectionsSection, PlaceholderSection


class SettingsWindow(QMainWindow):
    settings_applied = pyqtSignal()

    SECTIONS = [
        ("Общие", 24, "general"),
        ("Соединения", 33, "connections"),
        ("Озвучка чата", 32, "tts"),
        ("Озвучка донатов", 16, "donate_tts"),
        ("Звуки событий", 16, "event_sounds"),
        ("Тема оформления", 73, "general"),
        ("Hotkeys", 6, "general"),
        ("Валюта", 5, "general"),
        ("Прочее", 2, "general"),
    ]

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.CustomizeWindowHint)
        self.setWindowTitle("Chat_AG v1.0.3 - Настройки")
        self.setMinimumSize(900, 600)
        self.resize(900, 600)
        self.current_section_widget = None
        self._drag_pos = None

        central = QWidget()
        central.setStyleSheet(f"background-color: {COLORS['bg_main']};")
        self.setCentralWidget(central)

        main_lay = QVBoxLayout(central)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        self.title_bar = CustomTitleBar("Chat_AG - Настройки", self, show_extra_buttons=False)
        main_lay.addWidget(self.title_bar)

        content = QWidget()
        content.setStyleSheet(f"background-color: {COLORS['bg_main']};")
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(10, 10, 10, 10)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget()
        left.setStyleSheet(f"background-color: {COLORS['bg_main']};")
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(0, 0, 0, 0)

        self.sections_list = QListWidget()
        self.sections_list.setStyleSheet(LIST_STYLE)
        for name, count, _ in self.SECTIONS:
            self.sections_list.addItem(QListWidgetItem(f"{name} ({count})"))
        left_lay.addWidget(self.sections_list)
        splitter.addWidget(left)

        right = QWidget()
        right.setStyleSheet(f"background-color: {COLORS['bg_main']};")
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{ border: none; background-color: {COLORS['bg_main']}; }}
            QScrollBar:vertical {{ background-color: {COLORS['bg_secondary']}; width: 10px; border-radius: 5px; }}
            QScrollBar::handle:vertical {{ background-color: {COLORS['border']}; border-radius: 5px; min-height: 20px; }}
        """)
        right_lay.addWidget(self.scroll_area)
        splitter.addWidget(right)
        splitter.setSizes([250, 650])

        content_lay.addWidget(splitter)

        btns = QHBoxLayout()
        btns.addStretch()

        btn_cancel = QPushButton("Отмена")
        btn_cancel.setStyleSheet(BUTTON_DEFAULT)
        btn_cancel.clicked.connect(self.close)
        btns.addWidget(btn_cancel)

        btn_ok = QPushButton("ОК")
        btn_ok.setStyleSheet(BUTTON_ACCENT)
        btn_ok.clicked.connect(self._save_and_close)
        btns.addWidget(btn_ok)

        content_lay.addLayout(btns)
        main_lay.addWidget(content, stretch=1)

        self._load_section(0)
        self.sections_list.setCurrentRow(0)
        self.sections_list.currentRowChanged.connect(self._on_row_changed)

        screen = QApplication.primaryScreen()
        if screen:
            g = screen.geometry()
            self.move(max(0, (g.width() - self.width()) // 2),
                      max(0, (g.height() - self.height()) // 2))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Проверяем, что клик не по кнопкам и не по списку
            pos = event.pos()
            if (pos.y() < 40 and  # Клик в области заголовка
                    not self.sections_list.geometry().contains(pos) and
                    not self.scroll_area.geometry().contains(pos)):
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = None
        super().mouseReleaseEvent(event)

    def _on_row_changed(self, row):
        if row >= 0:
            self._load_section(row)

    def _load_section(self, row):
        if row < 0 or row >= len(self.SECTIONS):
            return

        if self.current_section_widget:
            old = self.scroll_area.widget()
            if old:
                old.setParent(None)
                old.deleteLater()
            self.current_section_widget = None

        name, count, section_id = self.SECTIONS[row]

        try:
            if section_id == "tts":
                self.current_section_widget = TTSSection()
            elif section_id == "donate_tts":
                self.current_section_widget = DonateTTSSection()
            elif section_id == "event_sounds":
                self.current_section_widget = EventSoundsSection()
            elif section_id == "connections":
                self.current_section_widget = ConnectionsSection()
                if hasattr(self.current_section_widget, 'connect_requested'):
                    self.current_section_widget.connect_requested.connect(self._on_connect_platform)
                if hasattr(self.current_section_widget, 'disconnect_requested'):
                    self.current_section_widget.disconnect_requested.connect(self._on_disconnect_platform)
            else:
                self.current_section_widget = PlaceholderSection(name)
        except Exception as e:
            print(f"⚠️ Ошибка загрузки секции {section_id}: {e}")
            import traceback
            traceback.print_exc()
            self.current_section_widget = PlaceholderSection(name)

        if self.current_section_widget:
            self.scroll_area.setWidget(self.current_section_widget)

    def _on_connect_platform(self, platform: str, config: dict):
        """Передать запрос на подключение в главное окно"""
        if self.main_window and hasattr(self.main_window, '_start_platform'):
            self.main_window._start_platform(platform, config)
            print(f"🔌 Запрос на подключение: {platform}")

    def _on_disconnect_platform(self, platform: str):
        """Передать запрос на отключение в главное окно"""
        if self.main_window and hasattr(self.main_window, '_stop_platform'):
            self.main_window._stop_platform(platform)
            print(f"🔌 Запрос на отключение: {platform}")

    def _save_and_close(self):
        if hasattr(self.current_section_widget, 'save_data'):
            try:
                self.current_section_widget.save_data()
                self.settings_applied.emit()
            except Exception as e:
                print(f"⚠️ Ошибка сохранения: {e}")
        self.close()

    def closeEvent(self, event):
        event.accept()