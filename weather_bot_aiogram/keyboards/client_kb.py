from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

button1 = KeyboardButton('/help')  # create keyboard button
kb_client = ReplyKeyboardMarkup(resize_keyboard=True)  # этот класс замещает обычную клавиатуру
                                                       # на созданную нами (button1)
kb_client.add(button1)