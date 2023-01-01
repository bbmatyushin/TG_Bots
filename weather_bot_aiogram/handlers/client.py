from aiogram import types, Dispatcher

from keyboards.client_kb import kb_client
from bot_classes.WeatherData import TGWeatherBot
from create_bot import bot

weather_data = TGWeatherBot()


#@dp.message_handler(commands=['start', 'help'])  # не нужет, т.к. handler зарегистрирован
async def command_start(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Hi there! Я могу сообщить о погоде в городах России.\n"
                           "Напишите название города.. только название ツ",
                           reply_markup=kb_client)


async def command_help(message: types.Message):
    await bot.send_message(message.from_user.id,
                           'Бот может сообщить о погоде в настоящий момент в любом городе России.')


async def handler_text(message: types.Message):
    await message.reply(weather_data.get_result(message.text))


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start'])
    dp.register_message_handler(command_help, commands=['help'])
    dp.register_message_handler(handler_text, content_types=['text'])