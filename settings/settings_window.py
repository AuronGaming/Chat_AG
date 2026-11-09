"""Окно настроек Chat_AG"""

from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout,
                             QListWidget, QListWidgetItem,
                             QWidget, QPushButton, QScrollArea, QSplitter,
                             QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from ui.theme_config import COLORS, BUTTON_DEFAULT, BUTTON_ACCENT, LIST_STYLE
from ui.custom_title_bar import CustomTitleBar


class SettingsWindow(QMainWindow):
    """Окно настроек приложения"""

    settings_applied = pyqtSignal()

    SECTIONS = [
        ("Общие", 24, "visual"),
        ("Соединения", 33, "connections"),
        ("Озвучивание текста", 32, "tts"),
        ("Система оповещений", 16, "alerts_system"),
        ("Оповещения в чате", 16, "chat_alerts"),
        ("Тема оформления", 73, "theme"),
        ("Hotkeys", 6, "hotkeys"),
        ("Валюта", 5, "currency"),
        ("Прочее", 2, "other"),
    ]

    def __init__(self, parent=None):
        super().__init__(None)  # Без родителя
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.CustomizeWindowHint)
        self.setWindowTitle("Chat_AG - Настройки")
        self.setMinimumSize(900, 600)
        self.resize(900, 600)

        self.current_section_widget = None

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

        btn_apply = QPushButton("Применить")
        btn_apply.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS['bg_input']}; color: {COLORS['accent']};
                border: 1px solid {COLORS['accent']}; border-radius: 4px; padding: 6px 16px;
                font-size: 13px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {COLORS['bg_hover']}; }}
        """)
        btn_apply.clicked.connect(self._apply_settings)
        btns.addWidget(btn_apply)

        btn_ok = QPushButton("ОК")
        btn_ok.setStyleSheet(BUTTON_ACCENT)
        btn_ok.clicked.connect(self._save_and_close)
        btns.addWidget(btn_ok)

        content_lay.addLayout(btns)
        main_lay.addWidget(content, stretch=1)

        # Загружаем первую секцию сразу
        self._load_section(0)

        self.sections_list.setCurrentRow(0)
        self.sections_list.currentRowChanged.connect(self._on_row_changed)

        self._center_on_screen()

    def _center_on_screen(self):
        screen = QApplication.primaryScreen()
        if screen:
            g = screen.geometry()
            self.move(max(0, (g.width() - self.width()) // 2),
                      max(0, (g.height() - self.height()) // 2))

    def _on_row_changed(self, row):
        if row >= 0:
            self._load_section(row)

    def _load_section(self, row):
        """Загрузить секцию по индексу"""
        if row < 0 or row >= len(self.SECTIONS):
            return

        # Удаляем старый виджет
        if self.current_section_widget:
            old = self.scroll_area.widget()
            if old:
                old.setParent(None)
                old.deleteLater()
            self.current_section_widget = None

        name, count, section_id = self.SECTIONS[row]

        try:
            if section_id == "visual":
                from settings.sections.visual.section import Section
            elif section_id == "connections":
                from settings.sections.connections.section import Section
            elif section_id == "tts":
                from settings.sections.tts.section import Section
            elif section_id == "alerts_system":
                from settings.sections.alerts_system.section import Section
            elif section_id == "chat_alerts":
                from settings.sections.chat_alerts.section import Section
            elif section_id == "theme":
                from settings.sections.theme.section import Section
            elif section_id == "hotkeys":
                from settings.sections.hotkeys.section import Section
            elif section_id == "currency":
                from settings.sections.currency.section import Section
            elif section_id == "other":
                from settings.sections.other.section import Section
            else:
                from settings.sections.placeholder import PlaceholderSection
                self.current_section_widget = PlaceholderSection(name)
                self.scroll_area.setWidget(self.current_section_widget)
                return

            self.current_section_widget = Section()
        except Exception as e:
            print(f"⚠️ Ошибка загрузки секции {section_id}: {e}")
            from settings.sections.placeholder import PlaceholderSection
            self.current_section_widget = PlaceholderSection(name)

        if self.current_section_widget:
            self.scroll_area.setWidget(self.current_section_widget)

    def _apply_settings(self):
        print("💾 Применение настроек...")
        if hasattr(self.current_section_widget, 'save_data'):
            try:
                self.current_section_widget.save_data()
                self.settings_applied.emit()
            except Exception as e:
                print(f"⚠️ Ошибка: {e}")

    def _save_and_close(self):
        print("💾 Сохранение настроек...")
        if hasattr(self.current_section_widget, 'save_data'):
            try:
                self.current_section_widget.save_data()
                self.settings_applied.emit()
            except Exception as e:
                print(f"⚠️ Ошибка: {e}")
        self.close()

    def closeEvent(self, event):
        event.accept()