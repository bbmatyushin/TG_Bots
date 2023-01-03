from aiogram import types, Dispatcher
from create_bot import bot
from postgres_db import diamonds_select as ds  # отвечает за выборку данных из таблиц


async def command_start(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Hi there! Бот хранит информацию об NFT коллекции TON-Diamonds, "
                           "которая выставлена на продажу на сайте http://ton.diamonds.\n"
                           "Укажите стоимость в **TON** и увидите топ-5 редких NFT за эту цену")


async def handler_text(message: types.Message):
    await message.reply(ds.get_result(client_price=message.text))


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start'])
    dp.register_message_handler(handler_text, content_types=['text'])