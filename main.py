import asyncio
import datetime

from telebot.async_telebot import AsyncTeleBot
from data import db_session
from data.users import User

bot = AsyncTeleBot('8519415006:AAH75sXe-k5eMGGqhsUUkeMRNHo2XSJKFfw')
db_session.global_init("db/blogs.db")
db_sess = db_session.create_session()


def add_user(username):
    if db_sess.get(User, username):
        return

    user = User(nickname=None, username=username)
    db_sess.add(user)
    db_sess.commit()


@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    text = "Добро пожаловать! Я бот, добавляющий экономику в стиле средневековья!"
    add_user(message.from_user.username)
    await bot.reply_to(message, text)


@bot.message_handler(commands=['profile', 'профиль'])
async def profile(message):
    user = db_sess.get(User, message.from_user.username)
    if user:
        update_user_data(user.username)
        text = f"""
{user.nickname if user.nickname else user.username}
Начало правления: {user.modified_data}
Деньги: {user.money}
Уровень экономики: {user.economy_level}
Уровень технологий: {user.technology_level}
Уровень исследователей: {user.researchers_level}
Воинов: {user.army}
Форты: {user.forts}
Секторы территории: {user.territory_sectors}
Коалиция: {user.coalition if user.coalition is not None else 'нет'}
"""
        await bot.reply_to(message, text)

    else:
        await send_not_found_user_message(message)


async def send_not_found_user_message(message):
    await bot.reply_to(message, 'Не найден! Напиши "/start" для того, чтобы начать править!')


def update_user_data(username):
    user = db_sess.get(User, username)
    if user:
        last_update_time = list(map(int,
                                    user.last_update.replace(' ', '-').replace(':', '-').split('.')[0].split('-') + [0])
                                )
        last_update_time = datetime.datetime(*last_update_time)
        hours_since_update = (datetime.datetime.now() - last_update_time).seconds // 3600
        if hours_since_update >= 1:
            user.money += user.economy_level * 50 * user.territory_sectors * hours_since_update
            user.army = min(user.forts * 100, user.army + user.forts * 25 * hours_since_update)
            user.last_update = datetime.datetime.now()
            db_sess.commit()



@bot.message_handler(commands=['set_nickname', 'установить_никнейм'])
async def set_nickname(message):
    user = db_sess.get(User, message.from_user.username)
    if user:
        nickname = message.text.split()[1]
        user.nickname = nickname
        db_sess.commit()
        await bot.reply_to(message, f'Никнейм успешно изменён на {nickname}')

    else:
        await send_not_found_user_message(message)

asyncio.run(bot.polling())