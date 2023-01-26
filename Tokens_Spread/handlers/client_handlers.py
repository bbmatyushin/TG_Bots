from aiogram import types, Dispatcher
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters.state import State, StatesGroup

from data_files.create_bot import bot, dp
from database.sqlite_select import SelectQuery
from data_files.useful_tools import UsefulTools


async def answer_all_messages(message: types.Message):
    currency_list = list(UsefulTools().get_currency_list().keys())
    if message.text.upper() in currency_list:
        sq = SelectQuery()
        await message.reply(sq.spread_output(table=message.text, symbol=message.text),
                            parse_mode='HTML')
    else:
        await message.answer("Нужно написать *тикер токена*, чтобы Бот выдал информацию по его "
                             "спреду на биржах.",
                             parse_mode='Markdown')


def reregister_handlers(dp: Dispatcher):
    dp.register_message_handler(answer_all_messages, content_types=['text'])


