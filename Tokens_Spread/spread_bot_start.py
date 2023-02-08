from aiogram.utils import executor

from data_files.create_bot import dp
from handlers import client_handlers


if __name__ == "__main__":
    executor.start_polling(dp, timeout=120, skip_updates=True)
