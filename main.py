import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from handlers import basic_handlers, info_handlers, create_handlers, war_handlers, delete_handlers
from functions import *

logging.basicConfig(level=logging.INFO)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(BOT_TOKEN)
dp = Dispatcher()


async def set_commands():
    commands = [
        types.BotCommand(command="start", description="Запустить бота"),
        types.BotCommand(command="help", description="Показать справку"),
        types.BotCommand(command="profile", description="Профиль"),
        types.BotCommand(command="profit", description="Доходы"),
        types.BotCommand(command="set_nickname", description="Установить никнейм"),
        types.BotCommand(command="coalition_profile", description="Профиль коалиции"),
        types.BotCommand(command="create_coalition", description="Создать коалицию"),
        types.BotCommand(command="disband", description="Распустить коалицию"),
        types.BotCommand(command="invite", description="Пригласить игрока в коалицию"),
        types.BotCommand(command="kick", description="Исключить игрока из коалиции"),
        types.BotCommand(command="build_fort", description="Построить форт"),
        types.BotCommand(command="hire_researcher", description="Нанять учёного"),
        types.BotCommand(command="develop_tech", description="Повысить уровень технологий"),
        types.BotCommand(command="develop_economy", description="Повысить уровень экономики"),
        types.BotCommand(command="settle_territory", description="Освоить сектор территорий"),
        types.BotCommand(command="buy_crystals", description="Купить кристаллы"),
        types.BotCommand(command="sell_crystals", description="Продать кристаллы"),
        types.BotCommand(command="crystals_rate", description="Курс кристаллов"),
        types.BotCommand(command="trade_agreement", description="Заключить торговое соглашение с игроком"),
        types.BotCommand(command="war_player", description="Объявить войну игроку"),
        types.BotCommand(command="attack", description="Атаковать игрока"),
        types.BotCommand(command="peace", description="Заключить мир с игроком"),

    ]
    await bot.set_my_commands(commands, scope=types.BotCommandScopeDefault())


async def main():
    await set_commands()
    task = asyncio.create_task(scheduler())
    dp.include_routers(basic_handlers.router, info_handlers.router, create_handlers.router, war_handlers.router,
                       delete_handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    task.cancel()


if __name__ == '__main__':
    asyncio.run(main())