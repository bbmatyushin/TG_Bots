from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from data_files.create_bot import bot, dp
from database.sqlite_select import SelectQuerySpread, SelectQueryPump
from data_files.useful_tools import UsefulTools
from keyboards.client_kb import kb_restart, ikb_choice, ikb_zazam


class FSMChoice(StatesGroup):
    choice_pump = State()
    choice_spread = State()
    zazam_spread = State()


@dp.message_handler(lambda msg: msg.text in ["Перезапустить"],
                    content_types=["text"], state="*")
async def command_restart(message: types.Message, state: FSMContext):
    await message.delete()
    await state.finish()
    await message.answer(text="Пшш.. пшшш... Бот на связи! 🫡\n\n"
                              "Выберите опцию:",
                         reply_markup=ikb_choice)


@dp.callback_query_handler(text=["pump"], state="*")
async def pump_message(callback: types.CallbackQuery):
    await FSMChoice.choice_pump.set()
    await callback.message.answer(text="Жду данных для анализа pump'ов...",
                                  reply_markup=kb_restart)
    await callback.answer()


@dp.callback_query_handler(text=["spread"], state="*")
async def spread_message(callback: types.CallbackQuery):
    await FSMChoice.choice_spread.set()
    await callback.message.answer(text="Жду данных для анализа спреда...",
                                  reply_markup=kb_restart)
    await callback.answer()


@dp.callback_query_handler(text=["neo_spread"], state="*")
async def spread_zazam(callback: types.CallbackQuery):
    await FSMChoice.zazam_spread.set()
    query_spread = SelectQuerySpread()
    output_result = query_spread.select_output_zazam()  #TODO: Передать объем торгов и % спреда
    part = len(output_result) // 4  # сообщение более 4096 симв, приходится дробить
    res1 = output_result[:part]
    res2 = output_result[part:part + part]
    res3 = output_result[part + part:part + part + part]
    res4 = output_result[part + part + part:]
    await callback.message.answer(text="".join(res1), parse_mode='HTML')
    await callback.message.answer(text="".join(res2), parse_mode='HTML')
    await callback.message.answer(text="".join(res3), parse_mode='HTML')
    if not res4:
        await callback.message.answer(text="Выберите следующую опцию:",
                                      reply_markup=ikb_choice)
    else:
        await callback.message.answer(text="".join(res4), parse_mode='HTML')
        await callback.message.answer(text="Выберите следующую опцию:",
                                      reply_markup=ikb_choice)


@dp.message_handler(lambda msg: msg.text.lower().startswith('my'), content_types=['text'],
                    state=FSMChoice.choice_pump)
async def get_my_best_change(message: types.Message):
    """Сообщение должно начинаться с my, потом через пробел
        1 значение - rank_min, 2 - rank_max"""
    data = message.text.lower().replace("my", "")
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
        await message.answer(sq_pump.best_change_output(rank_min=split_text[0]),
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



