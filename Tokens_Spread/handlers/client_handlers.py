from aiogram import types, Dispatcher
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters.state import State, StatesGroup

from data_files.create_bot import bot, dp
from database.sqlite_select import SelectQuery
from data_files.useful_tools import UsefulTools


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


def reregister_handlers(dp: Dispatcher):
    dp.register_message_handler(answer_all_messages, content_types=['text'])


