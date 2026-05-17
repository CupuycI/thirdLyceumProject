from aiogram import Router
from aiogram.filters.command import Command

from data.coalitions import Coalition
from functions import *

router = Router()


@router.message(Command("profile", "профиль"))
async def profile(message: types.Message):
    user = db_sess.get(User, message.from_user.id)
    if user:
        update_user_data(user)
        enemies = 'нет' if user.enemies is None else \
            [db_sess.get(User, id_) for id_ in user.enemies.replace(' ', '').split(',')]

        if enemies != 'нет':
            enemies = ', '.join([i.nickname if i.nickname is not None else i.username for i in enemies])
        text = f"""
{user.nickname if user.nickname else user.username}
👑 Начало правления: {user.modified_data}
🪙 Деньги: {user.money}
💎 Кристаллы: {user.crystals}
💰 Уровень экономики: {user.economy_level}
🛠️ Уровень технологий: {user.technology_level}
🧑‍🔬 Исследователи: {user.researchers}
🧪 Очки исследований: {user.research_points}
🥷 Воины: {user.army}
🏰 Форты: {user.forts}
🌲 Секторы территории: {user.territory_sectors}
🏛️ Коалиция: {user.coalition if user.coalition is not None else 'нет'}
👿 Противники: {enemies}
"""
        await message.answer(text)

    else:
        await send_not_found_user_message(message)


@router.message(Command('profit', 'доход'))
async def profit(message: types.Message):
    user = db_sess.get(User, message.from_user.id)
    if user:
        total = user.territory_sectors * 110 * user.economy_level - user.army - user.researchers
        agreements = 'нет'
        if user.trade_agreements is not None:
            agreements = ['']
            for i in user.trade_agreements.split(', '):
                trade = db_sess.get(TradeAgreement, int(i))
                second_user = db_sess.get(User, int(trade.second_user))
                agreements.append(f'\t\t\t\t+{trade.profit}. Заключён с {second_user.nickname if second_user.nickname 
                else second_user.username} '
                                  f'{trade.date}')
                total += trade.profit
            agreements = '\n'.join(agreements)
        text = f"""
Доходы:
\t\tСекторы территорий: +{user.territory_sectors * 110 * user.economy_level}
\t\tТорговые договоры: {agreements}
Расходы:
\t\tАрмия: -{user.army}
\t\tИсследователи: -{user.researchers}

Итого: {'+' if total > 0 else '' if total == 0 else '-'}{total}
"""
        await message.answer(text)

    else:
        await send_not_found_user_message(message)


@router.message(Command('coalition_profile', 'профиль_коалиции'))
async def coalition_profile(message: types.Message):
    text = message.text.split()
    if len(text) < 2 or not text[1]:
        await message.answer('❌ Неверное название!')
        return

    coalition = db_sess.get(Coalition, text[1])

    if not coalition:
        await message.answer('❌ Коалиция не найдена!')

    else:
        update_coalition_data(coalition)
        leader = db_sess.get(User, coalition.leader)
        members = 'нет' if coalition.members is None else [db_sess.get(User, int(id_)) for id_ in
                                                           coalition.members.replace(' ', '').split(',')]

        if members != 'нет':
            members = ', '.join([member.nickname if member.nickname is not None else member.username for member in
                                 members])
        if not leader:
            return

        text = f"""
{coalition.title}

👑 Лидер: {leader.nickname if leader.nickname is not None else leader.username}
👥 Участники: {members}
🥷 Армия: {coalition.army}
👿 Противники: {coalition.enemies if coalition.enemies else 'нет'}
Дата создания: {coalition.modified_data}
"""
        await message.answer(text)


@router.message(Command('crystals_rate', "курс_кристаллов"))
async def crystals_rate(message: types.Message):
    await message.answer(f"Курс кристаллов равен {get_crystal_rate()}")