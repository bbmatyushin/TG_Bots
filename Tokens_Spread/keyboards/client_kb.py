from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


kb_restart = ReplyKeyboardMarkup([
    [KeyboardButton(text='Перезапустить')]
],
    resize_keyboard=True, one_time_keyboard=True)

ikb_choice = InlineKeyboardMarkup(row_width=3)\
    .add(InlineKeyboardButton(text="Spread", callback_data="spread"),
         InlineKeyboardButton(text="Neo-spread", callback_data="neo_spread"),
         InlineKeyboardButton(text="Pump", callback_data="pump"))

ikb_zazam = InlineKeyboardMarkup(row_width=3)\
    .add((InlineKeyboardButton(text="Neo-spread", callback_data="zazam_spread")))
