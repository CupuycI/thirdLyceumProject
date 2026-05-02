import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from data.coalitions import Coalition
from handlers import basic_handlers, info_handlers, create_handlers, war_handlers
from functions import *

logging.basicConfig(level=logging.INFO)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(BOT_TOKEN)
dp = Dispatcher()
# db_session.global_init("db/blogs.db")
# db_sess = db_session.create_session()


async def main():
    dp.include_routers(basic_handlers.router, info_handlers.router, create_handlers.router, war_handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())