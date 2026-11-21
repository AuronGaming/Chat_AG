"""Настройки озвучки чата (TTS)"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QSlider, QHBoxLayout, QComboBox
from PyQt6.QtCore import Qt
from ui.theme_config import COLORS
from core.settings_manager import SettingsManager


class TTSSection(QWidget):
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

        self.cb_enabled = QCheckBox("Включить озвучку сообщений чата")
        self.cb_enabled.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 13px; font-weight: bold; spacing: 8px;")
        lay.addWidget(self.cb_enabled)

        voice_row = QHBoxLayout()
        voice_label = QLabel("Голос:")
        voice_label.setStyleSheet(f"color: {COLORS['text_primary']}; min-width: 80px; font-size: 13px;")
        voice_row.addWidget(voice_label)

        self.combo_voice = QComboBox()
        self.combo_voice.addItems(["Microsoft Irina Desktop - Russian", "Microsoft Pavel Desktop - Russian",
                                   "Microsoft Ekaterina Desktop - Russian"])
        self.combo_voice.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 13px;
                min-width: 200px;
            }}
        """)
        voice_row.addWidget(self.combo_voice, stretch=1)
        lay.addLayout(voice_row)

        volume_row = QHBoxLayout()
        volume_label = QLabel("Громкость:")
        volume_label.setStyleSheet(f"color: {COLORS['text_primary']}; min-width: 80px; font-size: 13px;")
        volume_row.addWidget(volume_label)

        self.slider_volume = QSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setMinimum(0)
        self.slider_volume.setMaximum(100)
        self.slider_volume.setValue(100)
        self.slider_volume.setStyleSheet(f"""
            QSlider::groove:horizontal {{ background: {COLORS['bg_input']}; height: 6px; border-radius: 3px; }}
            QSlider::handle:horizontal {{ background: {COLORS['accent']}; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px; }}
        """)
        volume_row.addWidget(self.slider_volume, stretch=1)

        self.label_volume = QLabel("100%")
        self.label_volume.setStyleSheet(f"color: {COLORS['text_primary']}; min-width: 40px; font-size: 13px;")
        volume_row.addWidget(self.label_volume)
        lay.addLayout(volume_row)
        self.slider_volume.valueChanged.connect(lambda v: self.label_volume.setText(f"{v}%"))

        speed_row = QHBoxLayout()
        speed_label = QLabel("Скорость:")
        speed_label.setStyleSheet(f"color: {COLORS['text_primary']}; min-width: 80px; font-size: 13px;")
        speed_row.addWidget(speed_label)

        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setMinimum(-10)
        self.slider_speed.setMaximum(10)
        self.slider_speed.setValue(0)
        self.slider_speed.setStyleSheet(f"""
            QSlider::groove:horizontal {{ background: {COLORS['bg_input']}; height: 6px; border-radius: 3px; }}
            QSlider::handle:horizontal {{ background: {COLORS['accent']}; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px; }}
        """)
        speed_row.addWidget(self.slider_speed, stretch=1)

        self.label_speed = QLabel("0")
        self.label_speed.setStyleSheet(f"color: {COLORS['text_primary']}; min-width: 40px; font-size: 13px;")
        speed_row.addWidget(self.label_speed)
        lay.addLayout(speed_row)
        self.slider_speed.valueChanged.connect(lambda v: self.label_speed.setText(str(v)))

        self.cb_ignore_short = QCheckBox("Игнорировать сообщения короче 3 символов")
        self.cb_ignore_short.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; spacing: 8px;")
        lay.addWidget(self.cb_ignore_short)

        self.cb_ignore_repeat = QCheckBox("Игнорировать повторяющиеся сообщения")
        self.cb_ignore_repeat.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; spacing: 8px;")
        lay.addWidget(self.cb_ignore_repeat)

        lay.addStretch()

    def save_data(self):
        s = SettingsManager()
        tts_settings = s.settings.get("tts", {})
        tts_settings['enabled'] = self.cb_enabled.isChecked()
        tts_settings['voice'] = self.combo_voice.currentText()
        tts_settings['volume'] = self.slider_volume.value()
        tts_settings['speed'] = self.slider_speed.value()
        tts_settings['ignore_short'] = self.cb_ignore_short.isChecked()
        tts_settings['ignore_repeat'] = self.cb_ignore_repeat.isChecked()
        s.settings["tts"] = tts_settings
        s.save()
        print("💾 Настройки озвучки чата сохранены")