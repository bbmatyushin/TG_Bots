import re
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from data_files.create_bot import bot, dp
from handlers.state_classes import FSMMain
from keyboards import kb_button as kb
from building_data.output_data import OutputData


@dp.message_handler(lambda msg: msg.text.lower() in ["старт", "start", "/start"],
                    content_types=["text"], state="*")
async def command_start(message: types.Message, state: FSMContext):
    await message.delete()
    await state.reset_data()
    await bot.send_message(message.from_user.id,
                           text="Бот на связи! 👋\n\n"
                                "Начните вводить название улицы, чтобы найти информацию по "
                                "интересующему вас дому.\n"
                                "Можно ввести первые 3-4 буквы для получения подсказки.\n\n"
                                "Информация берется с сайтов:\n"
                                "<a href='https://flatinfo.ru/'>FlatInfo</a>, "
                                "<a href='https://dom.mingkh.ru/'>ДОМ.МИНЖКХ</a>, "
                                "<a href='https://dom.mos.ru/Home'>Дома Москвы</a>.\n\n"
                                "❗️ Для перезапуска бота, отправьте в сообщении <b>старт</b> или <b>start</b>.",
                           parse_mode="HTML"
                           )
    await message.answer(text="Напишите название улицы:")
    await FSMMain.type_address_name.set()


@dp.message_handler(lambda msg: msg.text.lower() in ["🔎 начать поиск"],
                    content_types=["text"], state="*")
async def command_start(message: types.Message, state: FSMContext):
    await message.delete()
    await state.reset_data()
    await message.answer(text="Напишите название улицы:")
    await FSMMain.type_address_name.set()


@dp.message_handler(content_types=["text"], state=FSMMain.type_address_name)
async def get_streen_name(message: types.Message, state: FSMContext):
    if re.search(r'[a-zA-Z]{2,}', message.text):
       await message.reply(text="🚫 I don't understand English. "
                                "Please write me a message completely in Russian.")
    else:
        build_data = OutputData()
        async with state.proxy() as data:
            data["type_address_name"] = message.text
        address = data["type_address_name"]
        addr_data = build_data.get_addr_data(address=address)
        if isinstance(addr_data, list):
            if re.search('дом', addr_data[0]):
                await message.reply(text="❓ Уточните адрес:",
                                reply_markup=kb.get_address_kb(addr_list=addr_data))
            else:
                await message.reply(text="❓ Уточните улицу:",
                                reply_markup=kb.get_address_kb(addr_list=addr_data))
            await state.reset_data()
        elif isinstance(addr_data, dict):
            # может сразу прилететь объект dict с одним адресом,
            # тогда проверяем адрес из него совпадает с message.text
            # Пример: Москва, Мининский переулок
            address_search = message.text if message.text == addr_data["name"] else addr_data["name"]
            await message.answer(text=f"🔍 Начался сбор информации об объекте расположенному по адресу - "
                                      f"*{address_search}*", parse_mode='Markdown')
            await message.answer(build_data.get_output_result(addr_data_flainfo=addr_data,
                                                              full_address=address_search),
                                 parse_mode="HTML", reply_markup=kb.kb_start)
            await state.reset_data()
            await message.answer(text="Напишите название улицы:")
        else:
            await message.reply(text=f"👀 Не получилось найти данных по запросу *{message.text}*.\n",
                                parse_mode="Markdown")
            await state.reset_data()
