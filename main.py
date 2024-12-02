import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.database.models import async_main
from app.handlers import router


async def main():
    load_dotenv()
    token = os.getenv('TOKEN')
    await async_main()
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(
            main())
    except KeyboardInterrupt:
        print('Exit')
