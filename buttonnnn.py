# keyboards.py

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Admin panel keyboard
def admin_panel_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="To'y qo\'shish"),
                KeyboardButton(text="To'y o\'chirish")
            ],
            [
                KeyboardButton(text="To'y ro\'yxatini ko\'rish"),
                KeyboardButton(text="To'y ma\'lumotlarini yangilash"),
                KeyboardButton(text="📊 Statistika")

            ]
        ],
        resize_keyboard=True
    )
    return keyboard
