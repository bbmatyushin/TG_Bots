import logging
import timeit

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BadRequest

from logger.get_logs import LoggerForBot
from data_files.create_bot import bot, dp
from keyboards import client_kb as kb, kb_search
from data_files import  useful_tools as ut
from data_files.useful_tools import shipper_list_full_name
from calculation.shippers_calc import TotalTerminalResult
from handlers.state_classes import FSMMain

logger = LoggerForBot()

@dp.message_handler(lambda message: message.text in ['/start', '/help', 'Перезапустить'],
                    content_types=['text'], state="*")
async def command_start_help_restart(message: types.Message, state=None):
    LoggerForBot().message_logger_info(message)
    await message.delete()
    await state.reset_data()
    await bot.send_message(message.from_user.id,
                           f"Бот на связи! 👋\n\n"
                           f"Я могу помочь быстро рассчитать стоимость доставки груза "
                           f"и сравнить её между разными транспортными компаниями.\n\n"
                           f"Сейчас для сравнения доступны следующие ТК: *{', '.join(shipper_list_full_name)}*.",
                           parse_mode="Markdown",
                           reply_markup=kb.kb_restart)
    await FSMMain.shipment_choice_1.set()
    await bot.send_message(chat_id=message.from_user.id,
                           text="📍 Выберите способ доставки:",
                           reply_markup=kb.ikb_shipment_choice_1)


@dp.callback_query_handler(text=["to_address"], state=FSMMain.shipment_choice_1)
async def query_handling_prr(callback:types.CallbackQuery, state: FSMContext):
    logger.callback_logger_warn(callback)
    async with state.proxy() as data:
        data["delivery_derival_variant"] = 'terminal'
        data["delivery_arrival_variant"] = 'address'
    await callback.message.answer(text="📦 Требуется разгрузка на адресе доставки?",
                                 reply_markup=kb.ikb_handling)
    await FSMMain.handling.set()
    await callback.answer()


@dp.callback_query_handler(text=["handling_no", "handling_yes"], state=FSMMain.handling)
async def noactive_shipment_buttons(callback: types.CallbackQuery, state: FSMContext):
    logger.callback_logger_warn(callback)
    # await callback.message.answer(text="🛠 Кнопка пока в разработке 🔧⚙️",
    #                               reply_markup=kb.ikb_escape)
    async with state.proxy() as data:
        data["handling"] = 'yes' if callback.data == 'handling_yes' else 'no'
    await callback.message.answer(text=f"🏰 Напишите город отправителя:",
                                 parse_mode="Markdown")
    await FSMMain.derival_city.set()
    await callback.answer()


@dp.callback_query_handler(text="escape_button", state=FSMMain.shipment_choice_1)
async def escape_choice_shipment_method(callback: types.CallbackQuery):
    logger.callback_logger_warn(callback)
    await callback.message.delete()
    await callback.answer()


@dp.callback_query_handler(text="terminal_terminal", state=FSMMain.shipment_choice_1)
async def type_derival_city_simple_quick_calc(callback: types.CallbackQuery, state: FSMContext):
    logger.callback_logger_info(callback)
    async with state.proxy() as data:
        data["delivery_derival_variant"] = 'terminal'
        data["delivery_arrival_variant"] = 'terminal'
    await callback.message.answer(text=f"🏰 Напишите город отправителя:",
                                  parse_mode="Markdown")
    await FSMMain.derival_city.set()
    await callback.answer()


@dp.message_handler(content_types=['text'], state=FSMMain.derival_city)
async def query_derival_city(message: types.Message, state: FSMContext):
    logger.message_logger_info(message)
    norm_city_name = ut.change_city_name(message.text)
    if ut.check_cites_on_pop_list(norm_city_name):  # проверяем есть ли город в популярных...
        pass
    else:  # если нет то добавляем туда
        ut.save_popular_cites(norm_city_name)
    check_derival_city = ut.check_cites_on_pop_list(norm_city_name)
    if check_derival_city:
        if len(check_derival_city) == 1:
            async with state.proxy() as data:
                data["derival_city"] = norm_city_name
                data["derival_city_full_name"] = ''
            await message.answer("🏠 Напишите город получателя:")
            await FSMMain.arrival_city.set()
        else:
            try:
                await message.reply("Уточните вариант:",
                                    reply_markup=kb_search.get_kb(list(check_derival_city.keys())))
                async with state.proxy() as data:
                    data["check_derival_city"] = check_derival_city
                await FSMMain.check_derival_city.set()
            except BadRequest:
                await message.reply(text=f"👀 Найдено слишком много вариантов для *{norm_city_name}*.\n"
                                         f"Попробуйте ввести больше первых букв названия города.",
                                    parse_mode='Markdown')
    else:
        await message.reply(text=f"👀 Город *{norm_city_name}* не найден. Возможно опечатка.\n"
                                     f"Попробуйте ввести зановов или только первые буквы названия.",
                                parse_mode='Markdown')


@dp.message_handler(content_types=["text"], state=FSMMain.check_derival_city)
async def get_check_derival_city(message: types.Message, state: FSMContext):
    logger.message_logger_info(message)
    async with state.proxy() as data:
        check_derival_city = data["check_derival_city"]
    async with state.proxy() as data:
        data["derival_city"] = check_derival_city[message.text]["name"]
        data["derival_city_full_name"] = message.text
    await message.reply(text="Принял.", reply_markup=kb.kb_restart)
    await message.answer("🏠 Напишите город получателя:")
    await FSMMain.arrival_city.set()


@dp.message_handler(content_types=["text"], state=FSMMain.arrival_city)
async def query_arrival_city(message: types.Message, state: FSMContext):
    logger.message_logger_info(message)
    norm_city_name = ut.change_city_name(message.text)
    if ut.check_cites_on_pop_list(norm_city_name):  # проверяем есть ли город в популярных...
        pass
    else:  # если нет то добавляем туда
        ut.save_popular_cites(norm_city_name)
    check_arrival_city = ut.check_cites_on_pop_list(norm_city_name)
    if check_arrival_city:
        if len(check_arrival_city) == 1:
            async with state.proxy() as data:
                data["arrival_city"] = norm_city_name
                data["arrival_city_full_name"] = ''
            await message.answer("🧮 Выберите способ расчета:",
                                reply_markup=kb.ikb_simple_auto_or_manual)
            await FSMMain.calc_method_choice.set()
        else:
            await message.answer("Уточните вариант:",
                                 reply_markup=kb_search.get_kb(list(check_arrival_city.keys())))
            async with state.proxy() as data:
                data["check_arrival_city"] = check_arrival_city
            await FSMMain.check_arrival_city.set()
    else:
        await message.reply(text=f"👀 Город *{norm_city_name}* не найден. Возможно опечатка.\n"
                                 f"Попробуйте ввести зановов или только первые буквы названия.",
                            parse_mode='Markdown')


@dp.message_handler(content_types=["text"], state=FSMMain.check_arrival_city)
async def get_check_arrival_city(message: types.Message, state: FSMContext):
    logger.message_logger_info(message)
    async with state.proxy() as data:
        check_arrival_city = data["check_arrival_city"]
        data["arrival_city"] = check_arrival_city[message.text]["name"]
        data["arrival_city_full_name"] = message.text
    await message.reply(text="Принял.", reply_markup=kb.kb_restart)
    # await bot.edit_message_text(chat_id=message.from_user.id,
    #                             text="Выберите способ расчета:",
    #                             reply_markup=kb.ikb_simple_auto_or_manual)
    await message.answer("🧮 Выберите способ расчета:",
                         reply_markup=kb.ikb_simple_auto_or_manual)
    await FSMMain.calc_method_choice.set()


@dp.callback_query_handler(text="simple_quick_calc", state=FSMMain.calc_method_choice)
async def calc_simple_quick_method(callback: types.CallbackQuery, state: FSMContext):
    logger.callback_logger_info(callback)
    await callback.message.answer(text=f"🔎 Сравнивается стоимость доставки между ТК "
                                       f"*{', '.join(shipper_list_full_name)}*...\n"
                                       f"_(время сравнения ~6.3 сек.)_",
                                       parse_mode='Markdown')
    async with state.proxy() as data:
        delivery_derival_variant = data["delivery_derival_variant"]
        delivery_arrival_variant = data["delivery_arrival_variant"]
        derival_city_full_name = data["derival_city_full_name"]
        arrival_city_full_name = data["arrival_city_full_name"]
        handling = data["handling"] if data.get("handling") else 'no'
        result_answer = TotalTerminalResult()\
                .get_simple_result(derival_city=data["derival_city"], arrival_city=data["arrival_city"],
                                   derival_city_full_name=derival_city_full_name,
                                   arrival_city_full_name=arrival_city_full_name,
                                   delivery_derival_variant=delivery_derival_variant,
                                   delivery_arrival_variant=delivery_arrival_variant,
                                   handling=handling)

    await callback.message.answer(result_answer, parse_mode="Markdown")
    await callback.answer()

    await state.finish()  # выходим из машинного состояния
    await FSMMain.shipment_choice_1.set()  # и заходим обратно, ждём новое задание
    await callback.message.answer(text="📍 Выберите способ доставки:",
                                  reply_markup=kb.ikb_shipment_choice_1)


@dp.callback_query_handler(text="simple_features", state=FSMMain.calc_method_choice)
async def query_choice_quantity(callback: types.CallbackQuery):
    logger.callback_logger_info(callback)
    await callback.message.answer(text="🔢 Отправляется одно или несколько мест?",
                                  reply_markup=kb.ikb_quantity)
    await FSMMain.cargo_choice_quantity.set()
    await callback.answer()



#🚫❗️📍🏰🏘🚛🚚🧮🔎🔢👀