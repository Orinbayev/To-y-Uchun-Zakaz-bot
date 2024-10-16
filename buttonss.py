from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


admin_choice_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Musiqa qo'shish", callback_data="add_music"),
        InlineKeyboardButton(text="Kino qo'shish", callback_data="add_movie"),
    ]
])

# Admin panel keyboard
def admin_panel_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Kino qo'shish"), KeyboardButton(text="Musiqa qo'shish"),
            ],
            [
                KeyboardButton(text="Kino o'chirish"), KeyboardButton(text="Musiqa o'chirish"),
            ],
            [
                KeyboardButton(text="Kino ma'lumotlarini yangilash"), KeyboardButton(text="Musiqa ma'lumotlarini yangilash"),
            ],
            [
                KeyboardButton(text="Kino ro'yxatini ko'rish"), KeyboardButton(text="Musiqa ro'yxatini ko'rish"),
            ],
            [
                KeyboardButton(text="📊 Statistika"), 
            ]
        ],
        resize_keyboard=True
    )
    return keyboard




Chanel_id = [-1002176283267, -1002203281213, -1002203281213]

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot

KANALLAR = InlineKeyboardMarkup(
    inline_keyboard= [
        [InlineKeyboardButton(text='1-kanal', url='https://t.me/Avazoxun_orginal')],
        [InlineKeyboardButton(text='2-kanal', url='https://t.me/Jaloliddin_akhmadaliev')],
        [InlineKeyboardButton(text='2-kanal', url='https://t.me/Andijonda_NimaGap')],
        [InlineKeyboardButton(text='✅Tasdiqlash', callback_data='tasdiqlash')],
    ],  
    resize_keyboard=True
)

