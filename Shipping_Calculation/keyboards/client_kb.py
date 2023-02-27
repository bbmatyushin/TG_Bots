from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


""" =============  KeyBoards  ============= """
kb_restart = ReplyKeyboardMarkup([
    [KeyboardButton(text='Перезапустить')]
],
    resize_keyboard=True, one_time_keyboard=True)

""" =============  InlineKeyBoards  ============= """
"""Выбираем вид доставки"""
ikb_shipment_choice_1 = InlineKeyboardMarkup(row_width=2)\
    .add(InlineKeyboardButton(text="Межтерминальная", callback_data="terminal_terminal"),
         InlineKeyboardButton(text="Доставка до адреса", callback_data="to_address"))

"""Если доставка до адреса, то выбираем условия"""
ikb_shipment_choice_2 = InlineKeyboardMarkup(row_width=3)\
    .add(InlineKeyboardButton(text="Склад - Адрес", callback_data="terminal_address"),
         InlineKeyboardButton(text="Адрес - Склад", callback_data="address_terminal"),
         InlineKeyboardButton(text="Адрес - Адрес", callback_data="address_address"))

"""Расчитывать с параметрами по умолчанию или ввести вручную"""
ikb_simple_auto_or_manual = InlineKeyboardMarkup(row_width=2)
b1 = InlineKeyboardButton(text="Быстрый расчет", callback_data="simple_quick_calc")
b2 = InlineKeyboardButton(text="Ввести параметры", callback_data="simple_features")
ikb_simple_auto_or_manual.add(b1, b2)

"""Выбираем в чем будет заданы габариты"""
ikb_choice_size = InlineKeyboardMarkup(row_width=3)\
    .add(InlineKeyboardButton(text="мм", callback_data="mm"),
         InlineKeyboardButton(text="см", callback_data="sm"),
         InlineKeyboardButton(text="метр", callback_data="metr"))

"""Выбор количества мест"""
ikb_quantity = InlineKeyboardMarkup(row_width=2)\
    .add(InlineKeyboardButton(text="Одно место", callback_data="quantity_1"),
         InlineKeyboardButton(text="Несколько мест", callback_data="quantity_some"))

"""Выбор экспресс отправки или обычная"""
ikb_express = InlineKeyboardMarkup(row_width=2)\
    .add(InlineKeyboardButton(text="Обычная", callback_data="auto"),
         InlineKeyboardButton(text="Экспресс", callback_data="express"))

"""ПРР"""
ikb_handling = InlineKeyboardMarkup(row_width=2)\
    .add(InlineKeyboardButton(text="без ПРР", callback_data="handling_no"),
         InlineKeyboardButton(text="требуется ПРР", callback_data="handling_yes"))

"""Кнопка для возврата выбора вида доставки"""
ikb_escape = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text="Вернуться к выбору",
                                                                        callback_data="escape_button"))

