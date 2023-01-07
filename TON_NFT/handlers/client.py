from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext  # для объявл.анотации типов
from aiogram.dispatcher.filters.state import State, StatesGroup
from import_mylib.create_bot import bot, dp
from postgres_db import diamonds_select as ds  # отвечает за выборку данных из таблиц
from keyboards.client_kb import kb_client, inl_kb_collection, inl_kb_choice


class FSMChoice(StatesGroup):
    tbl_collection = State()
    show_result = State()


#  First display? command '/start'
async def command_start(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.from_user.id,
                           f"Hi there {message.from_user.first_name}! 👋\n"
                           f"Бот хранит информацию об NFT коллекции *TON-Diamonds*, "
                           f"которая выставлена на продажу "
                           f"на сайте [ton.diamonds](http://ton.diamonds).\n"
                           f"Укажите стоимость в *TON* и увидите топ-5 редких NFT за эту цену.\n"
                           f"Или вы можете указать параметр *редкость* и узнаете топ-5 NFT "
                           f"по стоимости с указанной вами редкостью.",
                           parse_mode='Markdown')
    await FSMChoice.tbl_collection.set()  # Бот переходит в режим FSM
    await bot.send_message(message.from_user.id,
                           f"""Выберите коллекцию:""",
                           reply_markup=inl_kb_collection)


async def command_restart(message: types.Message, state: FSMContext):
    await state.finish()
    await FSMChoice.tbl_collection.set()
    await bot.send_message(message.from_user.id, f"Hi there {message.from_user.first_name}! 👋\n"
                                                 f"Бот на связи ✌",
                           reply_markup=inl_kb_collection)


async def command_help(message: types.Message, state: FSMContext):
    await state.finish()
    await FSMChoice.tbl_collection.set()
    await bot.send_message(message.from_user.id, "Бот может показать топ-5 редких предметов из коллекции "
                                                 "*TON Diamonds* за ту стоимость, которую вы укажите.\n"
                                                 "Ещё он умееет находить самые дорогие предметы с той редкостью, "
                                                 "которую вы ему напишите.\n\n"
                                                 "*Для начала выберите коллекцию* 👇",
                           parse_mode='Markdown',
                           reply_markup=inl_kb_collection)


@dp.callback_query_handler(text='collection_choice', state="*")
async def choose_again(choose_again: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await FSMChoice.tbl_collection.set()
    await choose_again.message.answer("Доступные коллекции для отслеживания:",
                                      reply_markup=inl_kb_collection)
    await choose_again.answer()


# Написана для демонстрации, т.к. данных по этой коллекции нет
@dp.callback_query_handler(text='annihilation', state="*")
async def temporary_choice_collection(collection: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await FSMChoice.tbl_collection.set()
    await collection.answer('Пока нет данных по Annihilation. Эта кнопка сделана '
                            'для примера ツ')
    await collection.message.answer("Выберете, пожалуйста, другую коллекцию. Сейчас доступна "
                                    "только *TON Diamonds*",
                                    parse_mode='Markdown',
                                    reply_markup=inl_kb_collection)


@dp.callback_query_handler(text=['ton_diamonds'], state=FSMChoice.tbl_collection)
async def choice_collection(collection: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['tbl_collection'] = collection.data
    await FSMChoice.next()
    await collection.message.answer('Укажите стоимость или редкость:', reply_markup=inl_kb_choice)
    await collection.answer()

@dp.callback_query_handler(text=['current_price', 'rarity'], state=FSMChoice.show_result)
async def choice_result(choice: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['show_result'] = choice.data
    if data['show_result'] == 'current_price':
        await choice.message.answer("Напишите стоимость в TON:")
    elif data['show_result'] == 'rarity':
        await choice.message.answer("Напишите значение редкости:")
    await choice.answer()

# @dp.message_handler(content_types=['text'])
async def handler_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            condition = data['show_result']
            # table = data['tbl_collection']
            await message.reply(ds.get_select_result(client_message=message.text,
                                                     condition=condition),
                                parse_mode='HTML',
                                reply_markup=inl_kb_choice)
        except KeyError:
            await message.answer('❗Забыли нажать кнопку 👇', reply_markup=inl_kb_choice)
        await FSMChoice.show_result.set()
        # print(condition, table, message.text)
        # await message.answer('Укажите стоимость или редкость:', reply_markup=inl_kb_choice)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'старт'], state="*")
    dp.register_message_handler(command_restart, commands=['restart'], state="*")
    dp.register_message_handler(command_help, commands=['help', 'помощь'], state="*")
    dp.register_message_handler(handler_text, content_types=['text'], state=FSMChoice.show_result)
