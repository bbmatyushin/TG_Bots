from aiologger import Logger
from aiologger.levels import LogLevel
from aiologger.formatters.base import Formatter


class LoggerForBot:
    async def init_logger(self):
        formatter = Formatter('%(asctime)s [%(levelname)s] %(message)s')
        logger = Logger.with_default_handlers(name='ship_logger',
                                              formatter=formatter,
                                              level=LogLevel.INFO)

        return logger

    async def message_logger_info(self, message):
        logger = await self.init_logger()
        message_text = message.text.replace("\n", " ")
        logger.info(f'message from user_name={message.from_user.username} id={message.from_user.id} '
                    f'text={message_text}')

    async def message_logger_warn(self, message):
        logger = await self.init_logger()
        message_text = message.text.replace("\n", " ")
        logger.warning(f'message from user_name={message.from_user.username} id={message.from_user.id} '
                    f'text={message_text}')

    async def callback_logger_info(self, callback):
        logger = await self.init_logger()
        callback_message_text = callback.message.text.replace("\n", " ")
        logger.info(f'callback from user_name={callback.from_user.username} '
                    f'id={callback.from_user.id} '
                    f'callback_message_text={callback_message_text} '
                    f'callback_data={callback.data}')

    async def callback_logger_warn(self, callback):
        logger = await self.init_logger()
        callback_message_text = callback.message.text.replace("\n", " ")
        logger.warning(f'callback from user_name={callback.from_user.username} '
                       f'id={callback.from_user.id} '
                       f'callback_message_text={callback_message_text} '
                       f'callback_data={callback.data}')


if __name__ == "__main__":
    # format = '%(asctime)s [%(levelname)s] %(message)s'
    # sh = logging.StreamHandler()
    # fh = logging.FileHandler(filename='bot.log')
    # logging.basicConfig(handlers=(sh, fh), format=format,
    #                     datefmt='%m.%d.%Y %H:%M:%S', level=logging.INFO)
    #
    # logging.info("&&&")
    pass