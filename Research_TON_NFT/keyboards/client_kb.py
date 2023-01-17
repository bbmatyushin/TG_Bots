from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from import_modules import useful_tools as ut


""" =============  KeyBoards  ============= """
kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
b1 = KeyboardButton('/restart')
b2 = KeyboardButton('/help')

kb_client.row(b1, b2)

""" =============  InlineKeyBoards  ============= """
ikb_categories = InlineKeyboardMarkup(row_width=2)
ikb_trend_collect = InlineKeyboardMarkup(row_width=2)
ikb_popular_collect = InlineKeyboardMarkup(row_width=2)
ikb_result = InlineKeyboardMarkup(row_width=2)

# Button to start over
ib_main_cat = InlineKeyboardButton(text="Выбрать категорию", callback_data="choice_category")
ib_main_coll = InlineKeyboardButton(text="Выбрать коллекцию", callback_data="choice_collection")

# Categories button
ib1_cat = InlineKeyboardButton(text="В тренде", callback_data='сategory_trend')
ib2_cat = InlineKeyboardButton(text="Популярные", callback_data='сategory_popular')

# Collections button
# parameter 'callback_data' must be as name of the postgres table
# В text подставляется ключ из словаря коллекции, который соответсвует названию коллекции
# В callback_data - имя таблицы этой коллекции
ib1_tc = InlineKeyboardButton(text=str(list(ut.trend_collections().keys())[0]),
                              callback_data=str(ut.trend_tables_name()[0]))
ib2_tc = InlineKeyboardButton(text=str(list(ut.trend_collections().keys())[1]),
                              callback_data=str(ut.trend_tables_name()[1]))
ib3_tc = InlineKeyboardButton(text=str(list(ut.trend_collections().keys())[2]),
                              callback_data=str(ut.trend_tables_name()[2]))
ib4_tc = InlineKeyboardButton(text=str(list(ut.trend_collections().keys())[3]),
                              callback_data=str(ut.trend_tables_name()[3]))
ib5_tc = InlineKeyboardButton(text=str(list(ut.trend_collections().keys())[4]),
                              callback_data=str(ut.trend_tables_name()[4]))
ib6_tc = InlineKeyboardButton(text=str(list(ut.trend_collections().keys())[5]),
                              callback_data=str(ut.trend_tables_name()[5]))
ib7_tc = InlineKeyboardButton(text=str(list(ut.trend_collections().keys())[6]),
                              callback_data=str(ut.trend_tables_name()[6]))
ib8_tc = InlineKeyboardButton(text=str(list(ut.trend_collections().keys())[7]),
                              callback_data=str(ut.trend_tables_name()[7]))
ib9_tc = InlineKeyboardButton(text=str(list(ut.trend_collections().keys())[8]),
                              callback_data=str(ut.trend_tables_name()[8]))
ib10_tc = InlineKeyboardButton(text=str(list(ut.trend_collections().keys())[9]),
                              callback_data=str(ut.trend_tables_name()[9]))

ib1_pc = InlineKeyboardButton(text=str(list(ut.popular_collections().keys())[0]),
                              callback_data=str(ut.popular_tables_name()[0]))
ib2_pc = InlineKeyboardButton(text=str(list(ut.popular_collections().keys())[1]),
                              callback_data=str(ut.popular_tables_name()[1]))
ib3_pc = InlineKeyboardButton(text=str(list(ut.popular_collections().keys())[2]),
                              callback_data=str(ut.popular_tables_name()[2]))
ib4_pc = InlineKeyboardButton(text=str(list(ut.popular_collections().keys())[3]),
                              callback_data=str(ut.popular_tables_name()[3]))
ib5_pc = InlineKeyboardButton(text=str(list(ut.popular_collections().keys())[4]),
                              callback_data=str(ut.popular_tables_name()[4]))
ib6_pc = InlineKeyboardButton(text=str(list(ut.popular_collections().keys())[5]),
                              callback_data=str(ut.popular_tables_name()[5]))
ib7_pc = InlineKeyboardButton(text=str(list(ut.popular_collections().keys())[6]),
                              callback_data=str(ut.popular_tables_name()[6]))
ib8_pc = InlineKeyboardButton(text=str(list(ut.popular_collections().keys())[7]),
                              callback_data=str(ut.popular_tables_name()[7]))
ib9_pc = InlineKeyboardButton(text=str(list(ut.popular_collections().keys())[8]),
                              callback_data=str(ut.popular_tables_name()[8]))
ib10_pc = InlineKeyboardButton(text=str(list(ut.popular_collections().keys())[9]),
                              callback_data=str(ut.popular_tables_name()[9]))

# Results button
ib1_result = InlineKeyboardButton(text="Цена в TON", callback_data='price')
ib2_result = InlineKeyboardButton(text="Аналитика редкости", callback_data='rarity')
ib3_result = InlineKeyboardButton(text="Точечная аналитика редкости", callback_data='target_rarity')

# Choice categories
ikb_categories.add(ib1_cat, ib2_cat)

# Choice collections
ikb_trend_collect.add(ib1_tc, ib2_tc, ib3_tc, ib4_tc, ib5_tc,
                      ib6_tc, ib7_tc, ib8_tc, ib9_tc, ib10_tc).add(ib_main_cat)
ikb_popular_collect.add(ib1_pc, ib2_pc, ib3_pc, ib4_pc, ib5_pc,
                        ib6_pc, ib7_pc, ib8_pc, ib9_pc, ib10_pc).add(ib_main_cat)

# Choise result
ikb_result.add(ib1_result, ib2_result, ib3_result).row(ib_main_coll)

