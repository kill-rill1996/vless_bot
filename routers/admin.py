import time
from datetime import datetime

import pytz
from aiogram import Router, types
from aiogram.filters import Command

import routers.keyboards as kb
from routers import app, salt, messages as ms
from models import models


router = Router()
# router.message.middleware.register(CheckPrivateMessageMiddleware())


@router.message(Command("start"))
async def start_message(message: types.Message) -> None:
    """Команда /start"""
    msg = "Hello message"
    if type(message) == types.Message:
        await message.answer(msg)   # TODO add stickers
    else:
        await message.message.answer(msg) # TODO add stickers

    await app.service.login()

    await main_menu(message)


@router.callback_query(lambda callback: callback.data == "back-to-menu")
async def main_menu(message: types.Message | types.CallbackQuery):
    """Главное меню"""
    msg = "Главное меню"
    if type(message) == types.Message:
        await message.answer(msg, reply_markup=kb.main_keyboard().as_markup())
    else:
        await message.message.answer(msg, reply_markup=kb.main_keyboard().as_markup())


@router.callback_query(lambda callback: callback.data.split(salt)[1] == "users")
async def all_users_handler(callback: types.CallbackQuery) -> None:
    """Выводит всех пользователей"""
    all_users = await app.service.get_clients()

    await callback.message.edit_text("Список пользователей:", reply_markup=kb.all_users_keyboard(all_users).as_markup())


@router.callback_query(lambda callback: callback.data.split(salt)[0] == "user")
async def get_user_info_handler(callback: types.CallbackQuery) -> None:
    """Вывод информации по пользователю"""
    username = callback.data.split(salt)[1]
    client = await app.service.get_client(username)

    msg = await ms.client_info_message(client, app)
    await callback.message.edit_text(msg, reply_markup=kb.user_keyboard(client).as_markup())


# ADD USER
@router.callback_query(lambda callback: callback.data.split(salt)[1] == "new-user")
async def add_new_client(callback: types.CallbackQuery) -> None:
    """Добавление нового клиента"""
    client_model = models.ClientCreate(
        username=callback.from_user.username,   # TODO что делать если его нет
        tg_id=str(callback.from_user.id),
        is_active=True,
        expire_time=datetime.now(tz=pytz.timezone('Europe/Moscow')).timestamp() + 86_400 * 31   # TODO вместо заглушки нужно время по подписке
    )

    new_client = await app.service.create_new_client(client_model)

    # TODO хз как получить ссылку для клиента
    await callback.message.edit_text(f"Новый клиент создан успешно {new_client.username}!",
                                     reply_markup=kb.back_keyboard(f"main{salt}users").as_markup())





