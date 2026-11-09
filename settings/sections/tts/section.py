"""Раздел настроек 'Озвучивание текста'"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QSlider, QComboBox, QPushButton, QLineEdit)
from PyQt6.QtCore import Qt
from ui.theme_config import COLORS, INPUT_STYLE


class Section(QWidget):
    """Раздел настроек 'Озвучивание текста'"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(15, 10, 15, 10)
        lay.setSpacing(12)

        title = QLabel("Озвучка чата")
        title.setStyleSheet(f"font-size: 22px; color: {COLORS['accent']}; font-weight: bold;")
        lay.addWidget(title)

        sub = QLabel("Настройки голоса и параметров озвучки сообщений чата.")
        sub.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; padding-bottom: 10px;")
        lay.addWidget(sub)

        # Чекбокс включения
        self.enabled_checkbox = QCheckBox("Включить озвучку")
        self.enabled_checkbox.setStyleSheet(f"""
            QCheckBox {{ 
                color: {COLORS['text_primary']}; 
                font-size: 13px; 
                font-weight: bold;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 3px;
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['accent']};
            }}
        """)
        lay.addWidget(self.enabled_checkbox)

        # Выбор голоса
        voice_row = QHBoxLayout()
        voice_label = QLabel("Голос:")
        voice_label.setStyleSheet(f"color: {COLORS['text_primary']}; min-width: 80px; font-size: 13px;")
        voice_row.addWidget(voice_label)

        self.voice_combo = QComboBox()
        self.voice_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 13px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                selection-background-color: {COLORS['accent']};
                selection-color: white;
                border: 1px solid {COLORS['border']};
            }}
        """)
        voice_row.addWidget(self.voice_combo, stretch=1)
        lay.addLayout(voice_row)

        # Громкость
        volume_row = QHBoxLayout()
        volume_label = QLabel("Громкость:")
        volume_label.setStyleSheet(f"color: {COLORS['text_primary']}; min-width: 80px; font-size: 13px;")
        volume_row.addWidget(volume_label)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(100)
        self.volume_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {COLORS['bg_input']};
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['accent']};
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }}
        """)
        volume_row.addWidget(self.volume_slider, stretch=1)

        self.volume_label_value = QLabel("100%")
        self.volume_label_value.setStyleSheet(f"color: {COLORS['text_primary']}; min-width: 40px; font-size: 13px;")
        volume_row.addWidget(self.volume_label_value)
        lay.addLayout(volume_row)

        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_label_value.setText(f"{v}%")
        )

        # Скорость
        rate_row = QHBoxLayout()
        rate_label = QLabel("Скорость:")
        rate_label.setStyleSheet(f"color: {COLORS['text_primary']}; min-width: 80px; font-size: 13px;")
        rate_row.addWidget(rate_label)

        self.rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rate_slider.setMinimum(100)
        self.rate_slider.setMaximum(300)
        self.rate_slider.setValue(200)
        self.rate_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {COLORS['bg_input']};
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['accent']};
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }}
        """)
        rate_row.addWidget(self.rate_slider, stretch=1)

        self.rate_label_value = QLabel("200")
        self.rate_label_value.setStyleSheet(f"color: {COLORS['text_primary']}; min-width: 40px; font-size: 13px;")
        rate_row.addWidget(self.rate_label_value)
        lay.addLayout(rate_row)

        self.rate_slider.valueChanged.connect(
            lambda v: self.rate_label_value.setText(str(v))
        )

        # Шаблон
        template_row = QHBoxLayout()
        template_label = QLabel("Шаблон:")
        template_label.setStyleSheet(f"color: {COLORS['text_primary']}; min-width: 80px; font-size: 13px;")
        template_row.addWidget(template_label)

        self.template_field = QLineEdit()
        self.template_field.setPlaceholderText("$text")
        self.template_field.setStyleSheet(INPUT_STYLE)
        template_row.addWidget(self.template_field, stretch=1)
        lay.addLayout(template_row)

        # Чекбоксы mute
        self.mute_chat_checkbox = QCheckBox("Отключить озвучку чата")
        self.mute_chat_checkbox.setStyleSheet(f"""
            QCheckBox {{ color: {COLORS['text_primary']}; font-size: 13px; spacing: 8px; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 3px; background-color: {COLORS['bg_input']}; border: 1px solid {COLORS['border']}; }}
            QCheckBox::indicator:checked {{ background-color: {COLORS['accent']}; }}
        """)
        lay.addWidget(self.mute_chat_checkbox)

        self.mute_donate_checkbox = QCheckBox("Отключить озвучку донатов")
        self.mute_donate_checkbox.setStyleSheet(f"""
            QCheckBox {{ color: {COLORS['text_primary']}; font-size: 13px; spacing: 8px; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 3px; background-color: {COLORS['bg_input']}; border: 1px solid {COLORS['border']}; }}
            QCheckBox::indicator:checked {{ background-color: {COLORS['accent']}; }}
        """)
        lay.addWidget(self.mute_donate_checkbox)

        # Кнопка тест
        btn_test = QPushButton("🔊 Тест озвучки")
        btn_test.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #238636;
            }}
        """)
        btn_test.clicked.connect(self._test_speak)
        lay.addWidget(btn_test)

        lay.addStretch()

        self._load_voices()
        self._load_saved()

    def _load_voices(self):
        try:
            from tts.manager import TTSManager
            manager = TTSManager()
            voices = manager.get_voices_list()
            self.voice_combo.clear()
            for voice_id, voice_name in voices:
                self.voice_combo.addItem(voice_name, voice_id)
            print(f"🔊 Загружено голосов: {len(voices)}")
        except Exception as e:
            print(f"⚠️ Ошибка загрузки голосов: {e}")
            self.voice_combo.addItem("Недоступно", "")

    def _load_saved(self):
        from core.settings_manager import SettingsManager
        s = SettingsManager()
        tts = s.settings.get("tts", {})

        self.enabled_checkbox.setChecked(tts.get('enabled', False))
        self.volume_slider.setValue(tts.get('volume', 100))
        self.rate_slider.setValue(tts.get('speed', 200))
        self.template_field.setText(tts.get('template', '$text'))
        self.mute_chat_checkbox.setChecked(tts.get('mute_chat', False))
        self.mute_donate_checkbox.setChecked(tts.get('mute_donate', False))

        voice_id = tts.get('voice_id', '')
        if voice_id:
            for i in range(self.voice_combo.count()):
                if self.voice_combo.itemData(i) == voice_id:
                    self.voice_combo.setCurrentIndex(i)
                    break

    def _test_speak(self):
        try:
            from tts.manager import TTSManager
            manager = TTSManager()
            manager.enabled = True
            manager.speak("Тест озвучки Chat AG. Привет!")
            print("🔊 Тестовая озвучка запущена")
        except Exception as e:
            print(f"⚠️ Ошибка теста: {e}")

    def save_data(self):
        from core.settings_manager import SettingsManager
        s = SettingsManager()

        tts = s.settings.get("tts", {})
        tts['enabled'] = self.enabled_checkbox.isChecked()
        tts['volume'] = self.volume_slider.value()
        tts['speed'] = self.rate_slider.value()
        tts['template'] = self.template_field.text() or '$text'
        tts['mute_chat'] = self.mute_chat_checkbox.isChecked()
        tts['mute_donate'] = self.mute_donate_checkbox.isChecked()

        voice_id = self.voice_combo.currentData()
        if voice_id:
            tts['voice_id'] = voice_id

        s.settings["tts"] = tts
        s.save()

        try:
            from tts.manager import TTSManager
            manager = TTSManager()
            manager.enabled = tts['enabled']
            manager.mute_chat = tts['mute_chat']
            manager.mute_donate = tts['mute_donate']
            manager.set_volume(tts['volume'] / 100.0)
            manager.set_rate(tts['speed'])
            if voice_id:
                manager.set_voice(voice_id)
            manager.template = tts['template']
            print("💾 Настройки TTS сохранены")
        except Exception as e:
            print(f"⚠️ Ошибка применения TTS: {e}")