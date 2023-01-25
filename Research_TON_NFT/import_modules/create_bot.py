from aiogram import Bot
from aiogram.dispatcher import Dispatcher  # улавливает события в чате
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # Для передачи переменных между handlers

from import_modules.work_data_file import TOKEN_BOT


bot = Bot(token=TOKEN_BOT)
dp = Dispatcher(bot, storage=MemoryStorage())

# bot.get_new_session()