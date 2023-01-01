from aiogram.utils import executor  # для запуска бота в онлайн

from handlers import client
from create_bot import dp


async def on_startup(_):
    print('Bot online now!')


if __name__ == '__main__':
    client.register_handlers_client(dp)
    executor.start_polling(dp, skip_updates=True,  # skip_upd нужен, чтобы не засыпали бота сообщениями,
                           on_startup=on_startup)  # когда он не онлайн.


