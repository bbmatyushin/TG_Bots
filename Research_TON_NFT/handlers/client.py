from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext  # для объявл.анотации типов
from aiogram.dispatcher.filters.state import State, StatesGroup
from import_modules.create_bot import bot, dp

from keyboards.client_kb import ikb_categories, ikb_trend_collect, ikb_popular_collect, \
    ikb_result, kb_client
from import_modules import useful_tools as ut
from pg_database.select_queries import SelectResult


class FSMChoice(StatesGroup):
    choice_category = State()
    tbl_collection = State()
    show_result = State()


async def command_start_help(message: types.Message, state: FSMContext):
    await state.reset_data()
    await bot.send_message(message.from_user.id,
                           f"Hi there {message.from_user.first_name}! 👋\n"
                           f"Бот хранит информацию о трендовых и популяпных NFT коллекциях "
                           f"на блокчейне *TON*. "
                           f"С помощью бота можно отыскать недооцененные предметы "
                           f"из этих коллекций.\n\n"
                           f"Чтобы начать - выберите категорию нажав на кнопку ниже. "
                           f"Затем выберите коллекцию и укажите стоимость в *TON* "
                           f"и увидите *ТОП-5 редких NFT* за эту цену. "
                           f"Или вы можете указать параметр *редкость* и узнаете статистику "
                           f"по предметам с примерно такой же редкостью.",
                           parse_mode='Markdown')
    await FSMChoice.choice_category.set()  # Бот переходит в режим FSM
    await bot.send_photo(chat_id=message.from_user.id,
                         photo='https://tonblockchain.ru/content/images/size/w600/2022/02/photo_2022-01-25_19-50-29.jpg')
    await bot.send_message(message.from_user.id,
                           f"""*Выберите категорию:*""",
                           parse_mode='Markdown',
                           reply_markup=ikb_categories)


async def command_restart(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.from_user.id, f"Hi there {message.from_user.first_name}! 👋\n"
                                                 f"Бот на связи ✌\n\n"
                                                 f"Воспользуйся командой /help",
                           parse_mode='Markdown', reply_markup=kb_client)
    await bot.send_message(message.from_user.id, text="или *Выберите категорию:*",
                           parse_mode='Markdown', reply_markup=ikb_categories)
    await FSMChoice.choice_category.set()


@dp.callback_query_handler(text='choice_category', state="*")
async def choice_category(callback_q: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await FSMChoice.choice_category.set()
    await callback_q.message.answer(text="*Выберите одну из категорий:*",
                                    parse_mode='Markdown', reply_markup=ikb_categories)
    await callback_q.answer(cache_time=4)


@dp.callback_query_handler(text=['сategory_trend', 'сategory_popular'],
                           state=FSMChoice.choice_category)
async def user_category(callback_q: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['choice_category'] = callback_q.data
    await FSMChoice.next()
    if data['choice_category'] == 'сategory_trend':
        await callback_q.message.answer(text="Выберите одну из трендовых коллекций:",
                                        parse_mode='Markdown', reply_markup=ikb_trend_collect)
    elif data['choice_category'] == 'сategory_popular':
        await callback_q.message.answer(text="Выберите одну из популярных коллекций:",
                                        parse_mode='Markdown', reply_markup=ikb_popular_collect)
    await callback_q.answer(cache_time=4)


@dp.callback_query_handler(text=ut.all_tables_name(), state=FSMChoice.tbl_collection)
async def choice_collection(callback_q: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['tbl_collection'] = callback_q.data
    await FSMChoice.next()
    await callback_q.message.answer('Укажите стоимость или редкость:', reply_markup=ikb_result)
    await callback_q.answer(cache_time=4)


@dp.callback_query_handler(text=['price', 'rarity', 'target_rarity'],
                           state=FSMChoice.show_result)
async def show_result(callback_q: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['show_result'] = callback_q.data
    select_ = SelectResult()
    table = data['tbl_collection']
    min_price = select_.select_min_max_price(table=table)[0][0]
    max_price = select_.select_min_max_price(table=table)[0][1]
    count_subj = select_.select_min_max_price(table=table)[0][2]
    min_rarity = select_.select_max_min_rarity(table=table)[0][0]
    max_rarity = select_.select_max_min_rarity(table=table)[0][1]
    if count_subj in [None, 0, '0']:
        await callback_q.message.answer(f"Нет данных по этой коллекции. Возможно, стоит подождать, "
                                        f"когда они собирутся ¯\_(ツ)_/¯...")
    else:
        if data['show_result'] == 'price':
            await callback_q.message.answer(f"_Всего выставлено на продажу {count_subj:,} предметов "
                                            f"стоимостью от {min_price:,} до {max_price:,} TON_.\n\n"
                                            f"*Напишите стоимость в TON:*",
                                            parse_mode='Markdown')
        elif data['show_result'] == 'rarity':
            await callback_q.message.answer(f"_Редкость должна быть в диапазоне {min_rarity:,} - {max_rarity:,}_\n\n"
                                            f"*Напишите значение редкости:*",
                                            parse_mode='Markdown')
        elif data['show_result'] == 'target_rarity':
            await callback_q.message.answer(f"Напишите сначала *значение редкости* и после ❗️"
                                            f"*количество предметов* для анализа:\n\n"
                                            f"_(редкость должна быть в диапазоне {min_rarity:,} - {max_rarity:,}, "
                                            f"а количество предметов не больше {count_subj:,})_",
                                            parse_mode='Markdown')
            await callback_q.message.answer(f"✅ *Пример запроса:* _100 !15_", parse_mode='Markdown')

    await callback_q.answer(cache_time=4)


@dp.callback_query_handler(text='choice_collection', state=FSMChoice.show_result)
async def back_choice_coll(callback_q: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data['choice_category'] == 'сategory_trend':
            await callback_q.message.answer(text="Выберите одну из трендовых коллекций:",
                                            parse_mode='Markdown', reply_markup=ikb_trend_collect)
        elif data['choice_category'] == 'сategory_popular':
            await callback_q.message.answer(text="Выберите одну из популярных коллекций:",
                                            parse_mode='Markdown', reply_markup=ikb_popular_collect)
    await FSMChoice.tbl_collection.set()
    await callback_q.answer(cache_time=4)


async def handler_show_result(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            select_ = SelectResult()
            condition = data['show_result']
            table = data['tbl_collection']
            if condition == 'price':
                await message.reply(select_.get_top_5(client_message=message.text.replace(",", "."),
                                                      table=table,
                                                      condition=condition),
                                    parse_mode='HTML',
                                    reply_markup=ikb_result)
            elif condition == "rarity":
                await message.reply(select_.get_rarity_analytic(client_message=message.text.replace(",", "."),
                                                                table=table),
                                    parse_mode='HTML',
                                    reply_markup=ikb_result)
            elif condition == "target_rarity":
                try:
                    client_rarity = message.text.replace(",", ".").split('!')[0].strip()
                    dataset_count = float(message.text.replace(",", ".").split('!')[1].strip()) // 1
                    lower_limit = dataset_count // 2
                    upper_limit = dataset_count - lower_limit

                    await message.reply(select_.get_rarity_analytic(client_message=client_rarity,
                                                                    table=table, lower_limit=lower_limit,
                                                                    upper_limit=upper_limit),
                                        parse_mode='HTML',
                                        reply_markup=ikb_result)
                except:
                    await message.reply(f"🚫 Необходимо указать сначала редкость, потом количество предметов.\n\n"
                                        f"✅ *Пример запроса:* _100 !15_",
                                        parse_mode='Markdown')
        except KeyError:
            await message.answer('❗Забыли нажать кнопку 👇', reply_markup=ikb_result)
        # await FSMChoice.show_result.set()


async def handler_to_all(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            if data['choice_category'] == 'сategory_trend':
                await message.answer('Выберите одну из трендовых коллекций:',
                                     reply_markup=ikb_trend_collect)
            elif data['choice_category'] == 'сategory_popular':
                await message.answer(text="Выберите одну из популярных коллекций:",
                                     parse_mode='Markdown', reply_markup=ikb_popular_collect)
        except KeyError:
            await FSMChoice.choice_category.set()
            await message.answer('Нужно сначала *выбрать категорию* или воспользуйтесь командой /help.',
                                 parse_mode='Markdown',
                                 reply_markup=ikb_categories)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start_help, commands=['start', 'старт', 'help'], state="*")
    dp.register_message_handler(command_restart, commands=['restart'], state="*")
    dp.register_message_handler(handler_show_result, content_types=['text'], state="*")
    dp.register_message_handler(handler_to_all, content_types=['text'], state="*")
