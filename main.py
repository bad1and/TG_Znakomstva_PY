import asyncio
import os
import logging
import time

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.database.models import async_main
from app.handlers import router

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("bot.log", encoding="utf-8")
file_handler.setLevel(logging.ERROR)
file_formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(name)s - %(message)s")
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.CRITICAL)
console_formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


async def run_bot():
    load_dotenv()
    token = os.getenv('TOKEN')

    if not token:
        logger.critical("TOKEN не найден! Проверьте .env файл.")
        return

    await async_main()

    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)

    logger.critical("Бот запущен и начинает опрос Telegram API...")

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error("Ошибка в боте: %s", e, exc_info=True)
        raise  # Пробрасываем ошибку, чтобы она поймалась в `while True`


if __name__ == '__main__':
    while True:
        try:
            asyncio.run(run_bot())  # Запуск бота
            logger.critical("Бот запущен")
        except KeyboardInterrupt:
            logger.critical("Выход из бота через KeyboardInterrupt.")
            break  # Прерываем бесконечный цикл
        except Exception as e:
            logger.critical("Фатальная ошибка, перезапуск через 5 секунд...: %s", e, exc_info=True)
            time.sleep(5)  # Ожидание перед перезапуском
