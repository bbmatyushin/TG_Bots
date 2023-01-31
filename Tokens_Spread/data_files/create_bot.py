from aiogram import Bot
from aiogram.dispatcher import Dispatcher  # улавливает события в чате
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # Для передачи переменных между handlers

from data_files.data_file import BOT_TOKEN


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())