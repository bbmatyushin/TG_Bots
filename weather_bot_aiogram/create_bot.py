from aiogram import Bot
from aiogram.dispatcher import Dispatcher  # улавливает события в чате

from secret_keys import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)