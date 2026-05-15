import asyncio
import datetime
import json

import requests

from data import db_session
from data.trade_agreements import TradeAgreement
from data.users import User
from aiogram import types

db_session.global_init("db/blogs.db")
db_sess = db_session.create_session()


async def update_crystal_rate():
    address = "https://www.cbr-xml-daily.ru/daily_json.js"
    response = requests.get(address).json()

    with open('data/crystal_rate.json', 'w', encoding='utf8') as f:
        json.dump(int(response['Valute']['GBP']['Value']), f)


def get_crystal_rate() -> int:
    try:
        with open("data/crystal_rate.json", "r") as f:
            rate = json.load(f)

    except FileNotFoundError:
        update_crystal_rate()
        with open("data/crystal_rate.json", "r") as f:
            rate = json.load(f)

    return rate


async def get_crystals_from_message(message: types.Message) -> int | None:
    text = message.text.split()
    if len(text) < 2 or not text[1] or text[1].isalpha():
        await message.answer("❌ Не указано количество кристаллов!")
        return

    return int(text[1])


def add_user(message: types.Message):
    if db_sess.get(User, message.from_user.id):
        return

    user = User(id=message.from_user.id, nickname=message.from_user.first_name, username=message.from_user.username)
    db_sess.add(user)
    db_sess.commit()


def get_datetime(date):
    date = list(map(int,
                    str(date).replace(' ', '-').replace(':', '-').split('.'
                                                                            )[0].split('-') + [0])
                )
    return datetime.datetime(*date)


def delete_id(id_: str | int, string: str):
    string = string.replace(str(id_), '').replace(', ,', ', ')
    if not string.replace(' ', '').replace(',', ''):
        string = None

    return string


def update_user_data(user):
    if user:
        last_update_time = get_datetime(user.last_update)
        hours_since_update = (datetime.datetime.now() - last_update_time).seconds // 3600
        for hour in range(hours_since_update):
            user.money += user.economy_level * 110 * user.territory_sectors - user.army - user.researchers
            user.research_points += 10 * user.researchers
            if user.trade_agreements is not None:
                trades = [db_sess.get(TradeAgreement, int(i)) for i in user.trade_agreements.split(', ')]
                for i in trades:
                    if i:
                        if i.hours > 0:
                            i.hours -= 1
                            user.money += i.profit
                        else:
                            user.trade_agreements = delete_id(i.id, user.trade_agreements)
                            db_sess.delete(i)
                            db_sess.commit()
            if user.army < user.forts * 100:
                user.army = min(user.forts * 100, user.army + user.forts * 25)

            if user.money < 0:
                user.army -= 5
                if user.army < 0 and user.money < 0:
                    user.researchers -= 1

        user.last_update = datetime.datetime.now()
        db_sess.commit()


def update_coalition_data(coalition):
    if coalition:
        leader = db_sess.get(User, coalition.leader)
        army = leader.army
        enemies = leader.enemies
        if coalition.members is not None:
            for member in str(coalition.members).replace(' ', '').split(','):
                user = db_sess.get(User, int(member))
                if user:
                    update_user_data(user)
                    army += user.army
                    if user.enemies is not None:
                        enemies = f'{enemies}, {user.enemies}'

        coalition.army = army
        coalition.enemies = enemies
        db_sess.commit()


async def send_not_found_user_message(message: types.Message):
    await message.answer('❌ Не найден! Напиши "/start" для того, чтобы начать править!')


async def get_user(message: types.Message) -> User | None:
    text = message.text.split()

    if len(text) < 2 or not text[1]:
        await message.answer('❌ Неверный id игрока!')
        return

    if not text[1].isdigit():
        return db_sess.query(User).filter(User.username == text[1].replace('@', '')).first()

    return db_sess.get(User, int(text[1]))


async def wrong_button(callback_query: types.CallbackQuery):
    await callback_query.answer("❌ Не трогайте чужие кнопки!", show_alert=True)


async def scheduler():
    while True:
        await update_crystal_rate()
        await asyncio.sleep(3600)
