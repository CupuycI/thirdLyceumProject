from aiogram import Router, types
from aiogram.filters.command import Command
from functions import add_user

router = Router()


@router.message(Command("start", "help"))
async def send_welcome(message: types.Message):
    text = "Добро пожаловать! Я бот, добавляющий экономику в стиле средневековья!"
    add_user(message)
    await message.answer(text)