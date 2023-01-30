from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from data_files.create_bot import bot, dp
from keyboards.client_kb import kb
from data_files.shippers_and_cities_list import shipper_list, cities_list
from calculation.shippers_calc import TotalResult


class FSMShippingData(StatesGroup):
    derival_city = State()
    arrival_city = State()


async def command_start_help_restart(message: types.Message, state=None):
    await state.reset_data()
    await bot.send_message(message.from_user.id,
                           f"Бот на связи! 👋\n"
                           f"Я могу помочь быстро рассчитать стоимость доставки груза \n"
                           f"и сравнить её между разными транспортными компаниями.\n\n"
                           f"Сейчас для сравнения доступны следующие ТК: *{', '.join(shipper_list)}*.",
                           parse_mode="Markdown",
                           reply_markup=kb)
    await FSMShippingData.derival_city.set()
    await bot.send_message(chat_id=message.from_user.id,
                           text=f"🏘 Напишите город отправителя:",
                           parse_mode="Markdown")


async def get_derival_city(message: types.Message, state: FSMContext):
    if message.text.title() in cities_list:
        async with state.proxy() as data:
            data["derival_city"] = message.text
        await FSMShippingData.next()
        await message.reply("🏠 Напишите город получателя:")
    else:
        await message.reply(f"❌ Название города Боту неизвестно. "
                            f"Или в названии содержится опечатка ¯\_(ツ)_/¯\n\n"
                            f"Попробуйте ввести город отправителя ещё раз:")


async def get_arrival_city(message: types.Message, state: FSMContext):
    if message.text.title() in cities_list:
        async with state.proxy() as data:
            data["arrival_city"] = message.text

        result_answer = TotalResult().get_simple_result(derival_city=data["derival_city"],
                                                            arrival_city=data["arrival_city"])
        await message.answer(result_answer, parse_mode="Markdown")

        await state.finish()  # выходим из машинного состояния
        await FSMShippingData.derival_city.set()  # и заходим обратно, ждём новое задание
        await bot.send_message(chat_id=message.from_user.id,
                               text=f"🏘 Напишите город отправителя:",
                               parse_mode="Markdown")
    else:
        await message.reply(f"❌ Название города Боту неизвестно. "
                            f"Или в названии содержится опечатка ¯\_(ツ)_/¯\n\n"
                            f"Попробуйте ввести город получателя ещё раз:")


# async def command_restart()


def register_handlers(dp: Dispatcher):
    # dp.register_message_handler(command_start_help_restart,
    #                             commands=['start', 'help', 'restart'], state="*")
    dp.register_message_handler(command_start_help_restart,
                                lambda message: message.text in ['/start', '/help', 'Перезапустить'],
                                content_types=['text'], state="*")
    dp.register_message_handler(get_derival_city, content_types=['text'], state=FSMShippingData.derival_city)
    dp.register_message_handler(get_arrival_city, content_types=['text'], state=FSMShippingData.arrival_city)