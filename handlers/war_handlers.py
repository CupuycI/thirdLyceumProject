from aiogram import Router
from aiogram.filters.command import Command

from data.coalitions import Coalition
from functions import *

router = Router()


@router.message(Command('war_player', 'война_игроку'))
async def war_player(message: types.Message):

    enemy_user = await get_user(message)

    if not enemy_user:
        await message.answer('❌ Игрок не найден!')

    else:
        user = db_sess.get(User, message.from_user.id)
        if not user:
            await send_not_found_user_message(message)

        elif user.coalition is None or user.id == db_sess.get(Coalition, user.coalition).leader:
            if user.enemies is not None and str(enemy_user.id) in user.enemies:
                await message.answer(f'❌ Война {enemy_user.nickname if enemy_user.nickname is not None else
                enemy_user.username} уже объявлена!')
                return

            if enemy_user.id == user.id:
                await message.answer('❌ Вы не можете объявить войну себе!')
                return

            user.enemies = enemy_user.id if user.enemies is None else f'{user.enemies}, {enemy_user.id}'
            enemy_user.enemies = user.id if enemy_user.enemies is None else \
                f'{enemy_user.enemies}, {user.id}'

            db_sess.commit()

            await message.answer(f'{enemy_user.nickname if enemy_user.nickname is not None else
                enemy_user.username} объявлена война!')

        else:
            await message.answer('❌ Только лидер коалиции может объявлять войны!')


def fight(defender_user, attacker_user, attackers=False):
    update_user_data(defender_user)
    defenders = defender_user.army

    if not attackers:
        update_user_data(attacker_user)
        attackers = attacker_user.army

    if attacker_user.technology_level > defender_user.technology_level:
        defenders -= int(defenders / 100 * ((attacker_user.technology_level - defender_user.technology_level) * 5))

    elif defender_user.technology_level > attacker_user.technology_level:
        attackers -= int(attackers / 100 * (defender_user.technology_level - attacker_user.technology_level) * 5)

    if defenders > attackers:
        warriors = max(attackers // 5, attackers % 5)
        defenders -= warriors
        attackers -= warriors

    else:
        warriors = max(defenders // 5, defenders % 5)
        attackers -= warriors
        defenders -= warriors

    return defenders, warriors


@router.message(Command('attack', 'атаковать'))
async def attack(message: types.Message):

    enemy_user = await get_user(message)

    if not enemy_user:
        await message.answer('❌ Игрок не найден!')

    else:
        user = db_sess.get(User, message.from_user.id)
        if not user:
            await send_not_found_user_message(message)

        elif str(enemy_user.id) not in user.enemies and (user.coalition is None or str(enemy_user.id) in
                                                         db_sess.get(Coalition, user.coalition).enemies):
            await message.answer("❌ Нельзя напасть без объявления войны!")

        else:
            defenders, attackers = fight(enemy_user, user)
            if enemy_user.forts:
                attackers -= int(attackers / 100 * 5)

            coalition_text = ''
            if enemy_user.coalition and attackers:
                coalition_text = ['', 'Коалиция:']
                coalition = db_sess.get(Coalition, enemy_user.coalition)
                for member_id in coalition.members.split(', '):
                    if attackers <= 0:
                        attackers = 0
                        break
                    member = db_sess.get(User, int(member_id))
                    member_army = member.army
                    member.army, attackers = fight(member, user, attackers)
                    db_sess.commit()

                    coalition_text.append(f'\t\t{member.nickname if member.nickname else member.username}: '
                                          f'-{member_army - member.army} воинов')

                coalition_text = '\n'.join(coalition_text)

            enemy = enemy_user.nickname if enemy_user.nickname is not None else enemy_user.username
            attacker = user.nickname if user.nickname is not None else user.username

            if defenders > attackers:
                attackers //= 2
                defenders -= attackers
                fort_destroyed = False
                if enemy_user.army - defenders < enemy_user.army // 2 and enemy_user.forts:
                    enemy_user.forts -= 1
                    fort_destroyed = True

                text = f"""{enemy} победил!
                Итоги {enemy}:
                -{enemy_user.army - defenders} воинов
                {'-1 форт' if fort_destroyed else ''}
                
                Итоги {attacker}:
                -{user.army - attackers} воинов
                {coalition_text}"""

                enemy_user.army = defenders
                user.army = attackers
                db_sess.commit()

                await message.answer(text)

            else:
                attackers -= defenders // 2
                defenders //= 2
                fort_destroyed = False
                if enemy_user.forts:
                    enemy_user.forts -= 1
                    fort_destroyed = True

                money = enemy_user.money // enemy_user.territory_sectors
                enemy_user.territory_sectors = min(1, enemy_user.territory_sectors - 1)
                user.territory_sectors += 1
                enemy_user.money -= money
                user.money += money
                text = f"""{attacker} победил!
                Итоги {attacker}:
                -{user.army - attackers} воинов
                +1 сектор территорий 
                +{money} монет
                
                Итоги {enemy}:
                -{enemy_user.army - defenders} воинов
                {'-1 форт' if fort_destroyed else ''}
                -{money} монет
                -1 сектор территорий
                {coalition_text}"""

                user.army = attackers
                enemy_user.army = defenders
                db_sess.commit()

                await message.answer(text)
