from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from handlers.state_classes import FSMMain, FSMQuantitySome
from keyboards import client_kb as kb
from logger.get_logs import LoggerForBot
from data_files.useful_tools import shipper_list_full_name
from calculation.shippers_calc import TotalTerminalResult
from data_files.create_bot import dp, bot

# logger = LoggerForBot()


# @dp.callback_query_handler(text="quantity_some", state=FSMMain.cargo_choice_quantity)
async def query_cargo_quantity(callback: types.CallbackQuery):
    LoggerForBot().callback_logger_info(callback)
    await callback.message.answer(text="*Шаг [1/9]:*\n🔢 Укажите количество мест:",
                                 parse_mode='Markdown')
    await FSMQuantitySome.cargo_quantity.set()
    await callback.answer()


# @dp.message_handler(content_types=["text"], state=FSMQuantutySome.cargo_quantity)
async def query_cargo_dimensions_size(message: types.Message, state: FSMContext):
    LoggerForBot().message_logger_warn(message)
    async with state.proxy() as data:
        data["cargo_quantity"] = message.text.strip()
    await message.answer(text="*Шаг [2/9]:*\n📐 Выберите ед.изм. для размера груза:",
                         parse_mode='Markdown', reply_markup=kb.ikb_choice_size)
    await FSMQuantitySome.cargo_choice_size.set()


# @dp.callback_query_handler(text=["metr", "sm", "mm"], state=FSMQuantutySome.cargo_choice_size)
async def query_cargo_dimensions(callback: types.CallbackQuery, state: FSMContext):
    LoggerForBot().callback_logger_info(callback)
    async with state.proxy() as data:
        data["cargo_choice_size"] = callback.data
    if callback.data == "metr":
        example = "✅ _Пример: 0.3 0.45 1_"
    elif callback.data == 'sm':
        example = "✅ _Пример: 30 45 100_"
    else:
        example = "✅ _Пример: 300 450 1000_"
    
    await callback.message.answer(text=f"*Шаг [3/9]:*\n📦 Укажите через пробел Д×Ш×В самого большого места, "
                                       f"как в примере:\n\n"
                                       f"{example}", parse_mode='Markdown')
    await FSMQuantitySome.cargo_dimensions.set()
    await callback.answer()


# @dp.message_handler(content_types=["text"], state=FSMQuantitySome.cargo_dimensions)
async def query_cargo_most_weight(message: types.Message, state: FSMContext):
    cargo_dimensions_list = message.text.replace(",", ".").strip().split()
    if len(cargo_dimensions_list) != 3:
        LoggerForBot().message_logger_warn(message)
        await message.reply(text=f"🚫 Должно быть 3 размера груза, "
                                 f"а получено - {len(cargo_dimensions_list)}.\n"
                                 f"Попробуйте написать размеры ещё раз:",
                            reply_markup=kb.ikb_choice_size)
        await FSMQuantitySome.cargo_choice_size.set()
    else:
        LoggerForBot().message_logger_info(message)
        async with state.proxy() as data:
            data["cargo_dimensions"] = cargo_dimensions_list
            
        await message.answer(text="*Шаг [4/9]:*\n🏋🏻 Укажите самое тяжелое место в кг:",
                            parse_mode='Markdown')
        await FSMQuantitySome.cargo_most_weight.set()


# @dp.message_handler(content_types=["text"], state=FSMQuantutySome.cargo_most_weight)
async def query_cargo_total_weight(message: types.Message, state: FSMContext):
    LoggerForBot().message_logger_info(message)
    async with state.proxy() as data:
        data["cargo_most_weight"] = message.text.replace(",", ".").strip()
    await message.answer(text="*Шаг [5/9]:*\nУкажите общий вес груза в кг:",
                        parse_mode='Markdown')
    await FSMQuantitySome.cargo_total_weight.set()


# @dp.message_handler(content_types=['text'], state=FSMQuantutySome.cargo_total_weight)
async def query_cargo_total_volume(message: types.Message, state: FSMContext):
    LoggerForBot().message_logger_info(message)
    async with state.proxy() as data:
        data["cargo_total_weight"] = message.text.replace(",", ".").strip()
    await message.answer(text="*Шаг [6/9]:*\nУкажите общий объём груза в м3:",
                        parse_mode='Markdown')
    await FSMQuantitySome.cargo_total_volume.set()


# @dp.message_handler(content_types=["text"], state=FSMShippingData.cargo_total_volume)
async def query_total_volume(message: types.Message, state: FSMContext):
    LoggerForBot().message_logger_info(message)
    if message.text.replace(",", ".").replace(".", "").isdigit():
        async with state.proxy() as data:
            data["cargo_total_volume"] = message.text.replace(",", ".").strip()
        await message.answer(text="*Шаг [7/9]:*\n📑 Укажите стоимость груза, для расчета страховки:",
                            parse_mode='Markdown')
        await FSMQuantitySome.cargo_insurance.set()
    else:
        await message.reply(text="❌ Общий объём должен состоять только из цифр. Попробуйте ввести "
                                 "общий объём ещё раз:")
        
        
# @dp.message_handler(content_types=["text"], state=FSMQuantitySome.cargo_insurance)
async def query_temperature_mode(message: types.Message, state: FSMContext):
    LoggerForBot().message_logger_info(message)
    async with state.proxy() as data:
        data["cargo_insurance"] = message.text.strip()
    await message.answer(text="*Шаг [8/9]:*\n🌡 Груз нужно доставить в тепле?\n"
                              "_(доступно только для ЖДЭ)_",
                         parse_mode='Markdown', reply_markup=kb.ikb_temperature)
    await FSMQuantitySome.temperature.set()


# @dp.callback_query_handler(text=["temperature_no", "temperature_yes"], state=FSMQuantitySome.temperature)
async def query_express_status(callback: types.CallbackQuery, state: FSMContext):
    LoggerForBot().callback_logger_info(callback)
    async with state.proxy() as data:
        data["temperature"] = 'yes' if callback.data == 'temperature_yes' else 'no'
    await callback.message.answer(text="*Шаг [9/9]:*\n⚡️ Рассчитать стоимость для "
                                       "*обычной* доставки или *экспресс*?",
                                  parse_mode='Markdown', reply_markup=kb.ikb_express)
    await FSMQuantitySome.delivery_type.set()
    await callback.answer()


# @dp.callback_query_handler(text=["auto", "express"], state=FSMQuantitySome.delivery_type)
async def get_shipping_calc(callback: types.CallbackQuery, state: FSMContext):
    LoggerForBot().callback_logger_info(callback)
    async with state.proxy() as data:
        data["delivery_type"] = callback.data
        if data["cargo_choice_size"] == 'sm':
            lwh_list = list(map(lambda x: float(x)/100, data["cargo_dimensions"]))
            length, width, height = lwh_list[0], lwh_list[1], lwh_list[2]
        elif data["cargo_choice_size"] == 'mm':
            lwh_list = list(map(lambda x: float(x) / 1000, data["cargo_dimensions"]))
            length, width, height = lwh_list[0], lwh_list[1], lwh_list[2]
        else:
            length, width, height = \
                data["cargo_dimensions"][0], data["cargo_dimensions"][1], data["cargo_dimensions"][2]

        total_weight, total_volume, quantity, weight, insurance, delivery_type = \
            data["cargo_total_weight"], data["cargo_total_volume"], data["cargo_quantity"], \
                data["cargo_most_weight"], data["cargo_insurance"], data["delivery_type"]

        delivery_derival_variant = data["delivery_derival_variant"]
        delivery_arrival_variant = data["delivery_arrival_variant"]
        derival_city_full_name = data["derival_city_full_name"]
        arrival_city_full_name = data["arrival_city_full_name"]
        handling = data["handling"] if data.get("handling") else 'no'
        temperature = 'yes' if data.get("temperature") == 'yes' else 'no'

        str_answer = f"⏳ Сравнивается стоимость доставки между ТК " \
                     f"*{', '.join(shipper_list_full_name)}*...\n" \
                     f"_(время сравнения ~6.3 сек.)_" \
            if temperature == 'no' else \
            "⏳ Начался расчет стоимости доставки..."

    await callback.message.answer(text=f"{str_answer}",
                                  parse_mode='Markdown')

    result_answer = await TotalTerminalResult()\
        .get_simple_result(weight=weight, length=length, width=width, height=height,
                           quantity=quantity, total_weight=total_weight,
                           total_volume=total_volume, insurance=insurance,
                           delivery_type=delivery_type,
                           derival_city=data["derival_city"], arrival_city=data["arrival_city"],
                           delivery_derival_variant=delivery_derival_variant,
                           delivery_arrival_variant=delivery_arrival_variant,
                           derival_city_full_name=derival_city_full_name,
                           arrival_city_full_name=arrival_city_full_name,
                           handling=handling, temperature=temperature)
    await callback.message.answer(result_answer, parse_mode="Markdown")
    await callback.answer()
    await state.finish()  # выходим из машинного состояния
    await FSMMain.shipment_choice_1.set()  # и заходим обратно, ждём новое задание
    await callback.message.answer(text="📍 Выберите способ доставки:",
                                  reply_markup=kb.ikb_shipment_choice_1)


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(query_cargo_quantity, text="quantity_some",
                                       state=FSMMain.cargo_choice_quantity)
    dp.register_message_handler(query_cargo_dimensions_size, content_types=["text"],
                                state=FSMQuantitySome.cargo_quantity)
    dp.register_callback_query_handler(query_cargo_dimensions, text=["metr", "sm", "mm"],
                                       state=FSMQuantitySome.cargo_choice_size)
    dp.register_message_handler(query_cargo_most_weight, content_types=["text"],
                                state=FSMQuantitySome.cargo_dimensions)
    dp.register_message_handler(query_cargo_total_weight, content_types=["text"],
                                state=FSMQuantitySome.cargo_most_weight)
    dp.register_message_handler(query_cargo_total_volume, content_types=["text"],
                                state=FSMQuantitySome.cargo_total_weight)
    dp.register_message_handler(query_total_volume, content_types=["text"],
                                state=FSMQuantitySome.cargo_total_volume)
    dp.register_message_handler(query_temperature_mode, content_types=["text"],
                                state=FSMQuantitySome.cargo_insurance)
    dp.register_callback_query_handler(query_express_status, text=["temperature_no", "temperature_yes"],
                                       state=FSMQuantitySome.temperature)
    dp.register_callback_query_handler(get_shipping_calc, text=["auto", "express"],
                                       state=FSMQuantitySome.delivery_type)

#🚫❗️📍🏰🏘🚛🚚🧮🔎🔢👀