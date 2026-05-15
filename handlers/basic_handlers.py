from aiogram import Router, types
from aiogram.filters.command import Command
from functions import add_user

router = Router()


@router.message(Command("start", "help"))
async def send_welcome(message: types.Message):
    photo = types.FSInputFile("../data/welcome.png")
    text = """Добро пожаловать! Я бот, добавляющий экономику в стиле средневековья!
    Команды:
    ℹ️ /profile - профиль
    🪙 /profit - информация о доходах
    ✏️ /set_nickname <nickname> - установить никнейм
    ℹ️ /coalition_profile <coalition> - профиль коалиции
    🏛️ /create_coalition <coalition> - создать коалицию
    🔥 /disband - распустить коалицию
    📨 /invite <id/username> - пригласить игрока в коалицию
    🚪 /kick <id/username> - исключить игрока из коалиции
    🏰 /build_fort - построить форт
    🧑‍🔬 /hire_researcher - нанять учёного
    🛠️ /develop_tech - повысить уровень технологий
    💰 /develop_economy - повысить уровень экономики
    🌲 /settle_territory - освоить новый сектор территорий
    💎 /buy_crystals <count of crystals> - купить кристаллы
    💎 /sell_crystals <count of crystals> - продать кристаллы
    💎 /crystals_rate - получить курс кристаллов
    📜 /trade_agreement <id/username> - предложить игроку заключить торговый договор
    🗡️ /war_player <id/username> - объявить игроку войну
    ⚔️ /attack <id/username> - атаковать игрока
    🕊️ /peace <id/username> - предложить игроку заключить мир
    """
    add_user(message)
    await message.answer_photo(photo=photo)
    await message.answer(text=text)