from logger.get_logs import LoggerForBot
# from logger.get_logs import init_logger
from aiogram.utils import executor

from data_files.create_bot import dp, bot
from handlers import main_handlers, choice_quantity_one, choice_quantity_some


async def on_startup(_):
    # init_logger()
    logger = await LoggerForBot().init_logger()
    logger.warning("Bot is on the line!")


async def on_shutdown(_):
    logger = await LoggerForBot().init_logger()
    logger.warning("Bot shutdown.")


if __name__ == "__main__":
    choice_quantity_one.register_handlers(dp)
    choice_quantity_some.register_handlers(dp)
    executor.start_polling(dp, timeout=120, skip_updates=True,
                           on_startup=on_startup, on_shutdown=on_shutdown)
