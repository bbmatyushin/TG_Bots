from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
button1 = KeyboardButton('/restart')
button2 = KeyboardButton('/help')

kb_client.row(button1, button2)

"""========== Inline Keyboard =========="""
inl_kb_collection = InlineKeyboardMarkup(row_width=2)
inl_kb_choice = InlineKeyboardMarkup(row_width=2)

inl_main = InlineKeyboardButton(text='Выбрать коллекцию', callback_data='collection_choice')
inl_b1_collection = InlineKeyboardButton(text="TON Diamonds", callback_data='ton_diamonds')
inl_b2_collection = InlineKeyboardButton(text="Annihilation", callback_data='annihilation')
inl_b1_choice = InlineKeyboardButton(text="Цена в TON", callback_data='current_price')
inl_b2_choice = InlineKeyboardButton(text="Указать редкость", callback_data='rarity')

inl_kb_collection.add(inl_b1_collection, inl_b2_collection)
inl_kb_choice.add(inl_b1_choice, inl_b2_choice).add(inl_main)


urlkb = InlineKeyboardMarkup(row_width=2)
url_button1 = InlineKeyboardButton(text='yandex', url='http://yandex.com')
url_button2 = InlineKeyboardButton(text='google', url='https://google.com')

urlkb.add(url_button1, url_button2)

