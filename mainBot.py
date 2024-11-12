from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

import asyncio
import logging
import config

from routers import router as main_router
from DB.database import initialize_db

initialize_db()

bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()
dp.include_router(main_router)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    try:
        await dp.start_polling(bot)
    finally:
        pass

if __name__ == '__main__':
    asyncio.run(main())
