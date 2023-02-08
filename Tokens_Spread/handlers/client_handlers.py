from aiogram import types, Dispatcher
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters.state import State, StatesGroup

from data_files.create_bot import bot, dp
from database.sqlite_select import SelectQuery
from data_files.useful_tools import UsefulTools


@dp.message_handler(lambda x: x.text.startswith('#'), content_types=["text"])
async def get_best_change(message: types.Message):
    """Сообщение должно начинаться с #, потом через пробел
    1 значение - rank_min, 2 - rank_max, 3 - limit"""
    split_text = message.text.split()
    sq = SelectQuery()
    if len(split_text) == 4:
        await message.answer(sq.best_change_output(rank_min=split_text[1],
                                                   rank_max=split_text[2],
                                                   limit=split_text[3]),
                             parse_mode='Markdown')
    elif len(split_text) == 3:
        await message.answer(sq.best_change_output(rank_min=split_text[1],
                                                   rank_max=split_text[2],),
                             parse_mode='Markdown')
    elif len(split_text) == 2:
        await message.answer(sq.best_change_output(rank_min=split_text[1]),
                             parse_mode='Markdown')
    elif len(split_text) == 1:
        await message.answer(sq.best_change_output(),
                             parse_mode='Markdown')
    else:
        await message.reply(text="❌ Нет данных *¯\_(ツ)_/¯*",
                            parse_mode='Markdown')


@dp.message_handler(content_types=['text'])
async def answer_all_messages(message: types.Message):
    symbol = message.text.split()[0]
    currency_list = list(UsefulTools().get_currency_list().keys())
    if symbol.upper() in currency_list:
        sq = SelectQuery()
        if len(message.text.split()) > 1:
            volume = message.text.split()[1]
            if volume.isdigit():
                await message.reply(sq.spread_output(table=symbol, symbol=symbol,
                                                     volume=float(volume)),
                                    parse_mode='HTML')
        elif len(message.text.split()) == 1:
            await message.reply(sq.spread_output(table=symbol, symbol=symbol), parse_mode='HTML')
    else:
        await message.answer(f"Нужно написать *тикер токена*, чтобы Бот выдал информацию по его "
                             "спреду на биржах.",
                             parse_mode='Markdown')


