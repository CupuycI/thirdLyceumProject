from aiogram import Router
from aiogram.filters.command import Command

from data.coalitions import Coalition
from functions import *

router = Router()

@router.message(Command("kick", "кик"))
async def kick(message: types.Message):
    user = db_sess.get(User, message.from_user.id)
    if not user:
        await send_not_found_user_message(message)
        return

    if not user.coalition:
        await message.answer("❌ Вы не состоите в коалиции!")
        return

    coalition = db_sess.get(Coalition, user.coalition)

    if coalition.leader != user.id:
        await message.answer("❌ Вы не являетесь лидером коалиции!")
        return

    second_user = await get_user(message)
    if not second_user:
        await message.answer("❌ Игрок не найден!")
        return

    coalition.members = delete_id(second_user.id, coalition.members)
    second_user.coalition = None
    db_sess.commit()
    await message.answer(f"{'@' + second_user.username if second_user.username else 
    second_user.nickname if second_user.nickname else ''} исключён из коалиции!")


@router.message(Command("disband", "распустить"))
async def disband_coalition(message: types.Message):
    user = db_sess.get(User, message.from_user.id)
    if not user:
        await send_not_found_user_message(message)
        return

    if not user.coalition:
        await message.answer("❌ Вы не состоите в коалиции!")
        return

    coalition = db_sess.get(Coalition, user.coalition)

    if coalition.leader != user.id:
        await message.answer("❌ Вы не являетесь лидером коалиции!")
        return

    members = coalition.members[::]
    db_sess.delete(coalition)
    db_sess.commit()
    if members:
        for id_ in members.split(', '):
            member = db_sess.get(User, int(id_))
            if member:
                await message.answer(f"{'@' + member.username if member.username else 
                member.nickname if member.nickname else ''} коалиция распущена!")

    await message.answer(f"{'@' + user.username if user.username else
    user.nickname if user.nickname else ''} коалиция распущена!")


@router.message(Command('sell_crystals', 'продать_кристаллы'))
async def sell_crystals(message: types.Message):
    user = db_sess.get(User, message.from_user.id)
    if not user:
        await send_not_found_user_message(message)
        return

    crystals = await get_crystals_from_message(message)
    if not crystals:
        return

    if crystals > user.crystals:
        await message.answer(f"❌ Не хватает кристаллов! У вас {user.crystals} кристаллов!")
        return

    money = crystals * get_crystal_rate()
    user.money += money
    user.crystals -= crystals
    db_sess.commit()
    await message.answer(f'{crystals} кристаллов успешно продано за {money} монет!')
