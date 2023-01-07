from aiogram import Bot
from aiogram.dispatcher import Dispatcher  # улавливает события в чате
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # Для передачи переменных между handlers

from import_mylib.secret_keys import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())