from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.coalitions import Coalition
from data.trade_agreements import TradeAgreement
from functions import *
from main import bot

router = Router()


@router.message(Command('set_nickname', 'установить_никнейм'))
async def set_nickname(message: types.Message):
    user = db_sess.get(User, message.from_user.id)
    if user:
        nickname = message.text.split()[-1]
        user.nickname = nickname
        db_sess.commit()
        await message.answer(f'Никнейм успешно изменён на {nickname}')

    else:
        await send_not_found_user_message(message)


@router.message(Command('create_coalition', 'создать_коалицию'))
async def create_coalition(message: types.Message):
    user = db_sess.get(User, message.from_user.id)
    if user:
        if user.coalition is None:
            text = message.text.split()
            if len(text) < 2 or not text[1]:
                await message.answer('Неверное название!')

            elif db_sess.get(Coalition, text[1]):
                await message.answer('Коалиция уже существует!')

            else:
                coalition = Coalition(
                    title=text[1],
                    leader=user.id,
                    army=user.army,
                    enemies=user.enemies
                )

                db_sess.add(coalition)
                user.coalition = coalition.title
                db_sess.commit()

                await message.answer(f'Коалиция {coalition.title} успешно создана!')

        else:
            await message.answer('Уже состоите в коалиции!')

    else:
        await send_not_found_user_message(message)


@router.message(Command('invite', 'пригласить'))
async def invite_player(message: types.Message):
    user = db_sess.get(User, message.from_user.id)
    if not user:
        await send_not_found_user_message(message)
        return

    if not user.coalition:
        await message.answer('Вы не состоите в коалиции!')
        return

    coalition = db_sess.get(Coalition, user.coalition)
    if user.id != int(coalition.leader):
        await message.answer('Только лидер коалиции может приглашать других игроков!')
        return

    second_user = await get_user(message)

    if not second_user:
        await message.answer('Игрок не найден!')
        return

    if second_user.coalition:
        await message.answer('Игрок уже состоит в коалиции!')
        return

    if coalition.enemies and str(second_user.id) in coalition.enemies:
        await message.answer('Игрок является противником коалиции!')
        return

    invite_data = InviteCallback(
        first_user_id=user.id,
        second_user_id=second_user.id
    )
    await message.answer(
        f'Пригласить {'@' + second_user.username if second_user.username else second_user.nickname}?',
        reply_markup=await get_invite_choice(invite_data)
    )


class InviteCallback(CallbackData, prefix='invite'):
    first_user_id: int
    second_user_id: int


class InviteCallback2(CallbackData, prefix='invite2'):
    first_user_id: int
    second_user_id: int


async def get_invite_choice(invite_data: InviteCallback) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Нет", callback_data=f"invite_no:{invite_data.first_user_id}"),
                InlineKeyboardButton(text="Да", callback_data=invite_data.pack())
            ]
        ]
    )
    return  keyboard


@router.callback_query(F.data.startswith("invite_no:"))
async def invite_no_button(callback_query: types.CallbackQuery):
    if int(callback_query.data.split(':')[1]) != callback_query.from_user.id:
        await wrong_button(callback_query)
        return

    await callback_query.answer("Отмена")
    await callback_query.message.edit_text(
        "Отмена!",
        reply_markup=None
    )


@router.callback_query(InviteCallback.filter())
async def invite_yes_button(callback_query: types.CallbackQuery, callback_data: InviteCallback):
    if callback_query.from_user.id != callback_data.first_user_id:
        await wrong_button(callback_query)
        return

    user = db_sess.get(User, callback_data.first_user_id)
    second_user = db_sess.get(User, callback_data.second_user_id)

    await callback_query.message.answer(text=f"{'@' + second_user.username if second_user.username else 
    second_user.nickname if second_user.nickname else ''} принять приглашение в коалицию "
    f"{user.nickname if user.nickname is not None else '@' + user.username}({user.id})?",
    reply_markup=await get_invite_choice2(callback_data))
    await callback_query.answer("Приглашение отправлено!")
    await callback_query.message.edit_text(
        "Приглашение отправлено!",
        reply_markup=None)


async def get_invite_choice2(callback_data: InviteCallback):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Нет", callback_data=f"invite2_no:{callback_data.second_user_id}"),
                InlineKeyboardButton(text="Да", callback_data=InviteCallback2(
                    first_user_id=callback_data.first_user_id,
                    second_user_id=callback_data.second_user_id
                ).pack())
            ]
        ]
    )
    return keyboard


@router.callback_query(F.data.startswith("invite2_no:"))
async def invite2_no_button(callback_query: types.CallbackQuery):
    if callback_query.data.split(':')[1] != int(callback_query.from_user.id):
        await wrong_button(callback_query)
        return

    await callback_query.answer("Отмена")
    await callback_query.message.edit_text(
        "Отмена!",
        reply_markup=None
    )


@router.callback_query(InviteCallback2.filter())
async def invite2_yes_button(callback_query: types.CallbackQuery, callback_data: InviteCallback2):
    if callback_data.second_user_id != callback_query.from_user.id:
        await wrong_button(callback_query)
        return

    coalition = db_sess.get(Coalition, db_sess.get(User, callback_data.first_user_id).coalition)
    if not coalition.members:
        coalition.members = callback_data.second_user_id

    else:
        coalition.members += f', {callback_data.second_user_id}'

    await callback_query.message.edit_text(f'Приглашение принято! Добро пожаловать в коалицию {coalition.title}!')
    second_user = db_sess.get(User, callback_data.second_user_id)
    second_user.coalition = coalition.title
    update_coalition_data(coalition)
    db_sess.commit()


async def get_fort_choice(user_id) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Нет", callback_data=f"fort_no:{user_id}"),
                InlineKeyboardButton(text="Да", callback_data=f"fort_yes:{user_id}")
            ]
        ]
    )
    return keyboard


@router.callback_query(F.data.startswith("fort_no:"))
async def fort_no_button(callback_query: types.CallbackQuery):
    if int(callback_query.data.split(':')[1]) != callback_query.from_user.id:
        await wrong_button(callback_query)
        return

    await callback_query.answer("Отмена")
    await callback_query.message.edit_text(
    "Постройка отменена!",
    reply_markup=None
)


@router.callback_query(F.data.startswith("fort_yes:"))
async def fort_yes_button(callback_query: types.CallbackQuery):
    if int(callback_query.data.split(':')[1]) != callback_query.from_user.id:
        await wrong_button(callback_query)
        return

    user = db_sess.get(User, callback_query.from_user.id)
    update_user_data(user)
    if user.forts < user.territory_sectors:
        if user.money >= 350:
            user.forts += 1
            user.money -= 350
            db_sess.commit()
            await callback_query.answer("Форт построен!")
            await callback_query.message.edit_text(
                "Форт построен!",
                reply_markup=None)

        else:
            await callback_query.message.answer('Не хватает монет!')

    else:
        await callback_query.message.answer('Не хватает секторов территорий!')


@router.message(Command("build_fort", "построить_форт"))
async def build_fort(message: types.Message):
    user = db_sess.get(User, message.from_user.id)
    if not user:
        await send_not_found_user_message(message)
        return

    update_user_data(user)
    if user.forts < user.territory_sectors:
        if user.money >= 350:
            await message.answer(
                "Построить форт за 350 монет?",
                reply_markup=await get_fort_choice(message.from_user.id)
            )

        else:
            await message.answer('Не хватает монет!')

    else:
        await message.answer('Не хватает секторов территорий!')


class TradeAgreementCallback(CallbackData, prefix='trade'):
    first_user_id: int
    second_user_id: int
    necessary_money: int


@router.message(Command('trade_agreement', 'торговое_соглашение'))
async def trade_agreement(message: types.Message):
    user = db_sess.get(User, message.from_user.id)
    if not user:
        await send_not_found_user_message(message)
        return

    second_user = await get_user(message)

    if not second_user:
        await message.answer('Игрок не найден!')
        return

    if user.id == second_user.id:
        await message.answer('Нельзя заключить торговой договор с самим собой!')
        return

    else:
        necessary_money = (user.economy_level * user.territory_sectors * 100 +
                           second_user.economy_level * second_user.territory_sectors * 100) // 2

        print(message.message_id)
        await message.answer(
            f"Заключить торговый договор с "
            f"{second_user.nickname if second_user.nickname is not None else second_user.username}({second_user.id}) за"
            f" {necessary_money} монет?",
            reply_markup=await get_trade_choice(user.id, second_user.id, necessary_money)
        )


async def get_trade_choice(first_user_id, second_user_id, necessary_money) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Нет", callback_data=f"trade_no:{first_user_id}"),
                InlineKeyboardButton(text="Да", callback_data=TradeAgreementCallback(
                    first_user_id=first_user_id,
                    second_user_id=second_user_id,
                    necessary_money=necessary_money
                ).pack())
            ]
        ]
    )
    return keyboard


@router.callback_query(F.data.startswith("trade_no:"))
async def trade_no_button(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != int(callback_query.data.split(':')[1]):
        await wrong_button(callback_query)
        return

    await callback_query.answer("Отмена")
    await callback_query.message.edit_text(
    "Соглашение отменено!",
    reply_markup=None
    )


@router.callback_query(TradeAgreementCallback.filter())
async def trade_yes_button(callback_query: types.CallbackQuery, callback_data: TradeAgreementCallback):
    if callback_query.from_user.id != callback_data.first_user_id:
        await wrong_button(callback_query)
        return

    user = db_sess.get(User, callback_data.first_user_id)
    update_user_data(user)
    necessary_money = callback_data.necessary_money
    print(necessary_money)
    if user.money >= necessary_money:
        second_user = db_sess.get(User, callback_data.second_user_id)

        await callback_query.message.answer(text=f"{'@' + second_user.username if second_user.username else 
        second_user.nickname if second_user.nickname else ''} заключить торговый договор с "
        f"{user.nickname if user.nickname is not None else user.username}({user.id}) за"
        f" {necessary_money} монет?",
        reply_markup=await get_trade_agreement_choice(callback_data))
        await callback_query.answer("Заявка отправлена!")
        await callback_query.message.edit_text(
            "Заявка отправлена!",
            reply_markup=None)

    else:
        await callback_query.message.answer('Не хватает монет!')


class TradeAgreementCallback2(CallbackData, prefix='trade2'):
    first_user_id: int
    second_user_id: int
    necessary_money: int


async def get_trade_agreement_choice(callback_data: TradeAgreementCallback) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Нет", callback_data=f"trade_agreement_no:{callback_data.second_user_id}"),
                InlineKeyboardButton(text="Да", callback_data=TradeAgreementCallback2(
                    first_user_id=callback_data.first_user_id,
                    second_user_id=callback_data.second_user_id,
                    necessary_money=callback_data.necessary_money
                ).pack())
            ]
        ]
    )
    return keyboard


@router.callback_query(F.data.startswith("trade_agreement_no:"))
async def trade_agreement_no_button(callback_query: types.CallbackQuery):
    if int(callback_query.data.split(':')[1]) != callback_query.from_user.id:
        await wrong_button(callback_query)
        return

    await callback_query.answer("Заявка отклонена!")
    await callback_query.message.edit_text(
    "Заявка отклонена!",
    reply_markup=None
    )


@router.callback_query(TradeAgreementCallback2.filter())
async def trade_agreement_yes_button(callback_query: types.CallbackQuery, callback_data: TradeAgreementCallback):
    if callback_query.from_user.id != callback_data.second_user_id:
        await wrong_button(callback_query)
        return

    user = db_sess.get(User, callback_data.first_user_id)
    update_user_data(user)
    necessary_money = callback_data.necessary_money
    print(necessary_money)
    second_user = db_sess.get(User, callback_data.second_user_id)
    if second_user.money >= necessary_money and user.money >= necessary_money:
        agreement = TradeAgreement(
            profit=necessary_money // 4,
            second_user=second_user.id
        )
        db_sess.add(agreement)
        db_sess.commit()
        if user.trade_agreements is not None:
            user.trade_agreements += f', {agreement.id}'

        else:
            user.trade_agreements = str(agreement.id)

        agreement = TradeAgreement(
            profit=necessary_money // 4,
            second_user=user.id
        )
        db_sess.add(agreement)
        db_sess.commit()
        if second_user.trade_agreements is not None:
            second_user.trade_agreements += f', {agreement.id}'

        else:
            second_user.trade_agreements = str(agreement.id)

        second_user.money -= necessary_money
        user.money -= necessary_money

        db_sess.commit()

        await callback_query.answer("Заявка принята!")
        await callback_query.message.edit_text(
            "Заявка принята!",
            reply_markup=None)

    else:
        await callback_query.message.answer('Не хватает монет!')