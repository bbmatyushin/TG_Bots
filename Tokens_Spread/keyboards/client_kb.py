from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


ikb_choice = InlineKeyboardMarkup(row_width=3)\
    .add((InlineKeyboardButton(text="Spread", callback_data="spread")),
         InlineKeyboardButton(text="Pump", callback_data="pump"))
