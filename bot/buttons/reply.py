from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

async def admin_panel():
    rkb = ReplyKeyboardBuilder()
    rkb.button(text="Akkaunt qoshish🎦")
    rkb.button(text="Buyurtma berish 📢")
    rkb.button(text="Statistika 🛠")
    rkb.adjust(2, 1)
    return rkb.as_markup(resize_keyboard=True)

async def order_buttons():
    rkb = ReplyKeyboardBuilder()
    rkb.button(text="Obuna")
    rkb.button(text="Komment")
    rkb.button(text="Like")
    rkb.button(text="Ortga qaytish 🔙")
    rkb.adjust(2, 2)
    return rkb.as_markup(resize_keyboard=True)

async def back_button():
    rkb = ReplyKeyboardBuilder()
    rkb.button(text="Ortga qaytish 🔙")
    return rkb.as_markup(resize_keyboard=True)
