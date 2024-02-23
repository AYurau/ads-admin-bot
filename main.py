from aiogram import Bot, Dispatcher
import asyncio

from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN_API

bot = Bot(token=TOKEN_API, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher()


async def start():
    from handlers import router
    from handlers import get_start
    from handlers import scheduler

    dp.include_router(router)
    dp.message.register(get_start, Command(commands='start'))
    asyncio.create_task(scheduler())
    try:
        print('Бот запущен')
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
