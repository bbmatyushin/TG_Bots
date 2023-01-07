from aiogram.utils import executor

from handlers import client
from import_mylib.create_bot import dp


if __name__ == '__main__':
    client.register_handlers_client(dp)
    executor.start_polling(dp, skip_updates=True)