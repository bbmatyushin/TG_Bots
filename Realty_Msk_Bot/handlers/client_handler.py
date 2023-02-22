from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from data_files.create_bot import bot, dp
from handlers.state_classes import FSMMain
from keyboards import kb_button as kb
from building_data.output_data import OutputData

#

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
                                "<a href='https://dom.mos.ru/Home'>Дома Москвы</a>.",
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
    build_data = OutputData()
    async with state.proxy() as data:
        data["type_address_name"] = message.text
    address = data["type_address_name"]
    addr_data = build_data.get_addr_data(address=address)
    if isinstance(addr_data, list):
        await message.reply(text="Уточните адресс:",
                            reply_markup=kb.get_address_kb(addr_list=addr_data))
        await state.reset_data()
    elif isinstance(addr_data, dict):
        await message.answer(build_data.output_info(addr_data_flainfo=addr_data, full_address=address),
                             parse_mode="HTML", reply_markup=kb.kb_start)
        await state.reset_data()
        await message.answer(text="Напишите название улицы:")
        # await message.answer(text="Напишите название улицы:")
    else:
        await message.reply(text=f"Не получилось найти данных по запросу *{message.text}*.\n"
                           f"Попробуйте ещё раз.", parse_mode="Markdown")
        await state.reset_data()


