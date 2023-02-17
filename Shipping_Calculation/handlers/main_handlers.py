import logging
import timeit

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from logger.get_logs import LoggerForBot
from data_files.create_bot import bot, dp
from keyboards import client_kb as kb
from data_files.useful_tools import shipper_list_full_name
from calculation.shippers_calc import TotalTerminalResult
from handlers.state_classes import FSMMain

logger = LoggerForBot()


@dp.callback_query_handler(text=["to_address"], state=FSMMain.shipment_choice_1)
async def noactive_shipment_buttons(callback: types.CallbackQuery):
    logger.callback_logger_warn(callback)
    await callback.message.answer(text="🛠 Кнопка пока в разработке 🔧⚙️",
                                  reply_markup=kb.ikb_escape)
    await callback.answer()


@dp.callback_query_handler(text="escape_button", state=FSMMain.shipment_choice_1)
async def escape_choice_shipment_method(callback: types.CallbackQuery):
    logger.callback_logger_warn(callback)
    await callback.message.delete()
    await callback.answer()


@dp.callback_query_handler(text="terminal_terminal", state=FSMMain.shipment_choice_1)
async def type_derival_city_simple_quick_calc(callback: types.CallbackQuery):
    logger.callback_logger_info(callback)
    await callback.message.reply(text=f"🏰 Напишите город отправителя:",
                                 parse_mode="Markdown")
    await FSMMain.derival_city.set()
    await callback.answer()


@dp.message_handler(content_types=['text'], state=FSMMain.derival_city)
async def query_derival_city(message: types.Message, state: FSMContext):
    logger.message_logger_info(message)
    async with state.proxy() as data:
        data["derival_city"] = message.text
    await message.reply("🏠 Напишите город получателя:")
    await FSMMain.arrival_city.set()


@dp.message_handler(content_types=["text"], state=FSMMain.arrival_city)
async def query_arrival_city(message: types.Message, state: FSMContext):
    logger.message_logger_info(message)
    async with state.proxy() as data:
        data["arrival_city"] = message.text
    await message.reply(text="Выберите способ расчета:",
                        reply_markup=kb.ikb_simple_auto_or_manual)
    await FSMMain.calc_method_choice.set()


@dp.callback_query_handler(text="simple_quick_calc", state=FSMMain.calc_method_choice)
async def calc_simple_quick_method(callback: types.CallbackQuery, state: FSMContext):
    logger.callback_logger_info(callback)
    await callback.message.answer(text=f"🧮 Сравнивается стоимость доставки между ТК "
                                       f"*{', '.join(shipper_list_full_name)}*...\n"
                                       f"_(время сравнения ~6.3 сек.)_",
                                       parse_mode='Markdown')
    async with state.proxy() as data:
        result_answer = TotalTerminalResult().get_simple_result(derival_city=data["derival_city"],
                                                                arrival_city=data["arrival_city"])

    await callback.message.answer(result_answer, parse_mode="Markdown")
    await callback.answer()

    await state.finish()  # выходим из машинного состояния
    await FSMMain.shipment_choice_1.set()  # и заходим обратно, ждём новое задание
    await callback.message.answer(text="📍 Выберите способ доставки:",
                                  reply_markup=kb.ikb_shipment_choice_1)


@dp.callback_query_handler(text="simple_features", state=FSMMain.calc_method_choice)
async def query_choice_quantity(callback: types.CallbackQuery):
    logger.callback_logger_info(callback)
    await callback.message.answer(text="Отправляется одно или несколько мест?",
                                  reply_markup=kb.ikb_quantity)
    await FSMMain.cargo_choice_quantity.set()
    await callback.answer()



#🚫❗️📍🏰🏘🚛🚚