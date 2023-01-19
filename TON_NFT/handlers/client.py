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
                           f"Бот хранит информацию об NFT коллекциях, "
                           f"которые выставлена на продажу "
                           f"на сайте [TON.Diamonds](http://ton.diamonds).\n"
                           f"Выберите коллекцию и укажите стоимость в *TON* "
                           f"и увидите *ТОП-5 редких NFT* за эту цену. "
                           f"Или вы можете указать параметр *редкость* и узнаете статистику по предметам "
                           f"с примерно такой же редкостью.",
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
    await bot.send_message(message.from_user.id, "Бот может показать топ-5 редких предметов из коллекций "
                                                 "на сайте [TON.Diamonds](http://ton.diamonds) за ту стоимость, "
                                                 "которую вы укажите.\n"
                                                 "Ещё он умеет отображать статистику по предметам с той "
                                                 "редкостью, которую вы ему напишите.\n\n"
                                                 "*Для начала выберите коллекцию* 👇",
                           parse_mode='Markdown',
                           reply_markup=inl_kb_collection)


# Для проверки состояния значений state
async def command_state(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            if data['tbl_collection']:
                if data['show_result']:
                    await bot.send_message(message.from_user.id,
                                           f"Выбрана коллекция - {data['tbl_collection']}\n"
                                           f"Показывать результаты по - {data['show_result']}")
                else:
                    await bot.send_message(message.from_user.id,
                                       f"Выбрана только коллекция - {data['tbl_collection']}")
    except KeyError:
        await bot.send_message(message.from_user.id,
                               f"Пока ничего не выбрано или выбрана только коллекция ¯\_(ツ)_/¯")


@dp.callback_query_handler(text='collection_choice', state="*")
async def choose_again(choose_again: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await FSMChoice.tbl_collection.set()
    await choose_again.message.answer("Доступные коллекции для отслеживания:",
                                      reply_markup=inl_kb_collection)
    await choose_again.answer()


@dp.callback_query_handler(text=['ton_diamonds', 'annihilation', 'g_bot_sd',
                                 'stickerface_wearables', 'calligrafuturism_24_units'],
                           state=FSMChoice.tbl_collection)
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
    table = data['tbl_collection']
    min_price = ds.select_min_max_price(table)[0][0]
    max_price = ds.select_min_max_price(table)[0][1]
    count = ds.select_min_max_price(table)[0][2]
    min_rarity = ds.select_max_min_rarity(table)[0][0]
    max_rarity = ds.select_max_min_rarity(table)[0][1]
    if data['show_result'] == 'current_price':
        await choice.message.answer(f"_Всего выставлено на продажу {count} предметов "
                                    f"стоимостью от {min_price:,} до {max_price:,} TON_.\n\n"
                                    f"*Напишите стоимость в TON:*",
                                    parse_mode='Markdown')
    elif data['show_result'] == 'rarity':
        await choice.message.answer(f"Напишите сначала *значение редкости* и после ❗️"
                                    f"*количество предметов* для анализа:\n\n"
                                    f"_(редкость должна быть в диапазоне {min_rarity:,} - {max_rarity:,}, "
                                    f"а количество предметов не больше {count:,})_",
                                    parse_mode='Markdown')
        await choice.message.answer(f"✅ *Пример запроса:* _100 !15_", parse_mode='Markdown')
    await choice.answer()

# @dp.message_handler(content_types=['text'])
async def handler_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            condition = data['show_result']
            table = data['tbl_collection']
            if condition == 'current_price':
                await message.reply(ds.get_select_result_top_5(client_message=message.text,
                                                               table=table,
                                                               condition=condition),
                                    parse_mode='HTML',
                                    reply_markup=inl_kb_choice)
            if condition == 'rarity':
                # if len(message.text.split(',')) < 2:
                try:
                    client_rarity = message.text.replace(",", ".").split('!')[0].strip()
                    dataset_count = float(message.text.replace(",", ".").split('!')[1].strip()) // 1
                    lower_limit = dataset_count // 2
                    upper_limit = dataset_count - lower_limit
                    await message.reply(ds.get_select_result_rarity(client_message=client_rarity,
                                                                    table=table, lower_limit=lower_limit,
                                                                    upper_limit=upper_limit),
                                        parse_mode='HTML',
                                        reply_markup=inl_kb_choice)
                except:
                    await message.reply("❗️ Необходимо указать сначала редкость, потом количество предметов.\n\n"
                                        "✅ *Пример запроса:* _100 !15_", parse_mode='Markdown')
        except KeyError:
            await message.answer('❗Забыли нажать кнопку 👇', reply_markup=inl_kb_choice)
        await FSMChoice.show_result.set()
        # print(condition, table, message.text)
        # await message.answer('Укажите стоимость или редкость:', reply_markup=inl_kb_choice)

async def handler_to_all(message: types.Message):
    await message.answer('Нужно сначала выбрать коллекцию или воспользуйтесь командой /help.',
                         reply_markup=kb_client)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'старт'], state="*")
    dp.register_message_handler(command_restart, commands=['restart'], state="*")
    dp.register_message_handler(command_help, commands=['help', 'помощь'], state="*")
    dp.register_message_handler(command_state, commands=['state'], state="*")
    dp.register_message_handler(handler_text, content_types=['text'], state=FSMChoice.show_result)
    dp.register_message_handler(handler_to_all, content_types=['text'], state="*")
