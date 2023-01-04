from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

button1 = KeyboardButton('/restart')
button2 = KeyboardButton('/help')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

kb_client.row(button1, button2)