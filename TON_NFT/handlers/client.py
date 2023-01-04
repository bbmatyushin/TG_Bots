from aiogram import types, Dispatcher
from import_mylib.create_bot import bot
from postgres_db import diamonds_select as ds  # отвечает за выборку данных из таблиц
from keyboards.client_kb import kb_client


#  First display? command '/start'
async def command_start(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Hi there! 👋\nБот хранит информацию об NFT коллекции TON-Diamonds, "
                           "которая выставлена на продажу "
                           "на сайте [ton.diamonds](http://ton.diamonds).\n"
                           "Укажите стоимость в *TON* и увидите топ-5 редких NFT за эту цену.",
                           parse_mode='Markdown',
                           reply_markup=kb_client)


async def command_restart(message: types.Message):
    await bot.send_message(message.from_user.id, "Hi there! 👋\nБот на связи ✌",
                           reply_markup=kb_client)


async def command_help(message: types.Message):
    await bot.send_message(message.from_user.id, "Бот может показать топ-5 редких предметов из коллекции "
                                                 "*TON Diamonds* на ту стоимость, которую вы укажите.\n"
                                                 "Напишите *стоимость в TON* 👇",
                           parse_mode='Markdown')

async def handler_text(message: types.Message):
    await message.reply(ds.get_select_result(client_price=message.text), parse_mode='HTML')


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'старт'])
    dp.register_message_handler(command_restart, commands=['restart'])
    dp.register_message_handler(command_help, commands=['help', 'помощь'])
    dp.register_message_handler(handler_text, content_types=['text'])