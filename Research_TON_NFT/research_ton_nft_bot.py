from aiogram.utils import executor

from import_modules.create_bot import dp
from handlers import client


if __name__ == "__main__":
    client.register_handlers_client(dp)
    executor.start_polling(dp, skip_updates=True)