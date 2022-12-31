from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher  # уловливает события в чате
from aiogram.utils import executor  # для запуска бота в онлайн
from secret_keys import TOKEN
from bot_classes.WeatherData import TGWeatherBot

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
weather_data = TGWeatherBot()

async def on_startup(_):
    print('Bot online now!')


@dp.message_handler(commands=['start', 'help'])
async def command_start_help(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Hi there! Я могу сообщить о погоде в городах России.\n"
                           "Напишите название города.. только название ツ")


@dp.message_handler(content_types=['text'])
async def handle_text(message: types.Message):
    await message.reply(weather_data.get_result(message.text))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True,  # skip_upd нужен, чтобы не засыпали бота сообщениями,
                           on_startup=on_startup)  # когда он не онлайн.


