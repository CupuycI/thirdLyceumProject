import datetime

from data import db_session
from data.trade_agreements import TradeAgreement
from data.users import User
from aiogram import types

db_session.global_init("db/blogs.db")
db_sess = db_session.create_session()


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


def update_user_data(user):
    if user:
        last_update_time = get_datetime(user.last_update)
        hours_since_update = (datetime.datetime.now() - last_update_time).seconds // 3600
        if user.trade_agreements is not None:
            trades = [db_sess.get(TradeAgreement, int(i)) for i in user.trade_agreements.split(', ')]
        for hour in range(hours_since_update):
            user.money += user.economy_level * 110 * user.territory_sectors - user.army - user.researchers
            if user.trade_agreements is not None:
                for i in trades:
                    if i:
                        if i.hours > 0:
                            i.hours -= 1
                            user.money += i.profit
                        else:
                            user.trade_agreements = user.trade_agreements.replace(str(i.id), '').replace(', ,', ', ')
                            if not user.trade_agreements.replace(' ', '').replace(',', ''):
                                user.trade_agreements = None
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
    await message.answer('Не найден! Напиши "/start" для того, чтобы начать править!')


async def get_user(message: types.Message):
    text = message.text.split()

    if len(text) < 2 or not text[1]:
        await message.answer('Неверный id игрока!')
        return

    if not text[1].isdigit():
        return db_sess.query(User).filter(User.username == text[1].replace('@', '')).first()

    return db_sess.get(User, int(text[1]))

async def wrong_button(callback_query: types.CallbackQuery):
    await callback_query.answer("❌ Не трогайте чужие кнопки!", show_alert=True)