from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


kb = ReplyKeyboardMarkup([
    [KeyboardButton(text='Перезапустить')]
],
    resize_keyboard=True, one_time_keyboard=True)

# kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
# b1 = KeyboardButton(text='restart')
# b2 = KeyboardButton(text="")
#
# kb.add(b1)