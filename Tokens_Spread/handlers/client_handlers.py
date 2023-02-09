from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from data_files.create_bot import bot, dp
from database.sqlite_select import SelectQuerySpread, SelectQueryPump
from data_files.useful_tools import UsefulTools
from keyboards.client_kb import ikb_choice


class FSMChoice(StatesGroup):
    choice_pump = State()
    choice_spread = State()


@dp.callback_query_handler(text=["pump"], state="*")
async def pump_message(callback: types.CallbackQuery):
    await FSMChoice.choice_pump.set()
    await callback.message.answer(text="Жду данных для анализа pump'ов...")
    await callback.answer()


@dp.callback_query_handler(text=["spread"], state="*")
async def pump_message(callback: types.CallbackQuery):
    await FSMChoice.choice_spread.set()
    await callback.message.answer(text="Жду данных для анализа спреда...")
    await callback.answer()


@dp.message_handler(lambda msg: msg.text.startswith('my'), content_types=['text'],
                    state=FSMChoice.choice_pump)
async def get_my_best_change(message: types.Message):
    """Сообщение должно начинаться с my, потом через пробел
        1 значение - rank_min, 2 - rank_max"""
    data = message.text.replace("my", "")
    split_text = data.strip().split()
    sq_pump = SelectQueryPump()
    if len(split_text) == 2:
        await message.answer(sq_pump.best_change_output_to_me(rank_max=split_text[0],
                                                        rank_min=split_text[1]),
                             parse_mode='Markdown')
    elif len(split_text) == 1:
        await message.answer(sq_pump.best_change_output_to_me(rank_min=split_text[0]),
                             parse_mode='Markdown')
    elif not split_text:
        await message.answer(sq_pump.best_change_output_to_me(),
                             parse_mode='Markdown')
    else:
        await message.reply(text="❌ Нет данных *¯\_(ツ)_/¯*",
                            parse_mode='Markdown')
    await message.answer(text="Жду новых данных...\n"
                              "или можно переключиться на другую опцию:",
                         reply_markup=ikb_choice)


@dp.message_handler(content_types=["text"], state=FSMChoice.choice_pump)
async def get_best_change(message: types.Message):
    """Через пробел передать
    1 значение - rank_max, 2 - rank_min, 3 - limit"""
    split_text = message.text.split()
    sq_pump = SelectQueryPump()
    if len(split_text) == 3:
        await message.answer(sq_pump.best_change_output(rank_max=split_text[0],
                                                        rank_min=split_text[1],
                                                        limit=split_text[2]),
                             parse_mode='Markdown')
    elif len(split_text) == 2:
        await message.answer(sq_pump.best_change_output(rank_max=split_text[0],
                                                   rank_min=split_text[1]),
                             parse_mode='Markdown')
    elif len(split_text) == 1:
        await message.answer(sq_pump.best_change_output(),
                             parse_mode='Markdown')
    else:
        await message.reply(text="❌ Нет данных *¯\_(ツ)_/¯*",
                            parse_mode='Markdown')
    await message.answer(text="Жду новых данных...\n"
                              "или можно переключиться на другую опцию:",
                         reply_markup=ikb_choice)


@dp.message_handler(content_types=['text'], state=FSMChoice.choice_spread)
async def answer_all_messages(message: types.Message):
    symbol = message.text.split()[0]
    currency_list = list(UsefulTools().get_currency_list().keys())
    if symbol.upper() in currency_list:
        sq_spread = SelectQuerySpread()
        if len(message.text.split()) > 1:
            volume = message.text.split()[1]
            if volume.isdigit():
                await message.reply(sq_spread.spread_output(table=symbol, symbol=symbol,
                                                            volume=float(volume)),
                                    parse_mode='HTML')
        elif len(message.text.split()) == 1:
            await message.reply(sq_spread.spread_output(table=symbol, symbol=symbol),
                                parse_mode='HTML')
    else:
        await message.answer(f"Нужно написать *тикер токена*, чтобы Бот выдал информацию по его "
                             "спреду на биржах.",
                             parse_mode='Markdown')
    await message.answer(text="Жду новых данных...\n"
                              "или можно переключиться на другую опцию:",
                         reply_markup=ikb_choice)


@dp.message_handler(content_types=["text"], state="*")
async def restart(message: types.Message, state: FSMContext):
    await state.finish()
    await message.delete()
    await bot.send_message(chat_id=message.from_user.id,
                           text=f"Hi, {message.from_user.username}! 👋\n\n"
                                f"*Сначала выбери опцию:*",
                           parse_mode='Markdown',
                           reply_markup=ikb_choice)



