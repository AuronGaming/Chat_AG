"""Генерация иконки Chat_AG"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_chat_ag_icon(size=256):
    """Создать иконку AG с черным фоном и зелеными буквами"""

    # Создаем изображение
    img = Image.new('RGBA', (size, size), (0, 0, 0, 255))  # Черный фон
    draw = ImageDraw.Draw(img)

    # Рисуем зеленый круг (опционально, для красоты)
    margin = size // 16
    draw.ellipse([margin, margin, size - margin, size - margin],
                 fill=(0, 0, 0, 255),
                 outline=(34, 197, 94, 255),  # Зеленая обводка
                 width=size // 32)

    # Текст "AG"
    text = "AG"

    # Пробуем загрузить жирный шрифт
    try:
        font_size = size // 2
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

    # Центрируем текст
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (size - text_width) // 2
    y = (size - text_height) // 2 - size // 16  # Чуть выше центра

    # Рисуем текст зеленым цветом
    draw.text((x, y), text, fill=(34, 197, 94, 255), font=font)  # #22c55e

    # Сохраняем PNG
    png_path = os.path.join(os.path.dirname(__file__), 'chat_ag_icon.png')
    img.save(png_path)
    print(f"✅ PNG иконка создана: {png_path}")

    # Конвертируем в ICO (для Windows)
    ico_path = os.path.join(os.path.dirname(__file__), 'chat_ag_icon.ico')
    img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"✅ ICO иконка создана: {ico_path}")

    return png_path, ico_path


if __name__ == "__main__":
    create_chat_ag_icon(256)