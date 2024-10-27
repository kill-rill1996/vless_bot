import time
from datetime import datetime

import pytz
from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

import routers.keyboards as kb
from fsm_states import AddUserByAdminFSM
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
        # при отмене
        if message.data == "cancel":
            await message.message.answer(msg, reply_markup=kb.main_keyboard().as_markup())
        # при нажатии кнопки назад
        else:
            await message.message.edit_text(msg, reply_markup=kb.main_keyboard().as_markup())


@router.callback_query(lambda callback: callback.data != "cancel" and callback.data.split(salt)[1] == "users")
async def all_users_handler(callback: types.CallbackQuery) -> None:
    """Выводит всех пользователей"""
    all_users = await app.service.get_clients()

    await callback.message.edit_text("Список пользователей:", reply_markup=kb.all_users_keyboard(all_users).as_markup())


@router.callback_query(lambda callback: callback.data != "cancel" and callback.data.split(salt)[0] == "user")
async def get_user_info_handler(callback: types.CallbackQuery) -> None:
    """Вывод информации по пользователю"""
    username = callback.data.split(salt)[1]
    client = await app.service.get_client(username)

    msg = await ms.client_info_message(client, app)
    await callback.message.edit_text(msg, reply_markup=kb.user_keyboard(client).as_markup())


# ADD USER BY ADMIN
@router.callback_query(lambda callback: callback.data != "cancel" and callback.data.split(salt)[1] == "new-user")
async def add_new_client_by_admin(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Добавление нового клиента админом, начало FSM AddUserByAdmin"""
    await state.set_state(AddUserByAdminFSM.contact)
    msg = await callback.message.edit_text(
        "Отправьте карточку контакта нового администратора через вкладку 'Прикрепить'",
        reply_markup=kb.cancel_keyboard().as_markup()
    )
    await state.update_data(prev_mess=msg)


@router.message(~F.content_type.in_({'contact'}), AddUserByAdminFSM.contact)
async def wrong_contact_data(message: types.Message, state: FSMContext) -> None:
    """Если отправлена не карточка контакта"""
    data = await state.get_data()
    try:
        await data["prev_mess"].delete()
    except TelegramBadRequest:
        pass

    msg = await message.answer("Необходимо отправить <b>карточку контакта</b> через вкладку 'Прикрепить'",
                               reply_markup=kb.cancel_keyboard().as_markup())
    await state.update_data(prev_mess=msg)


@router.message(F.contact, AddUserByAdminFSM.contact)
async def save_new_client_by_admin(message: types.Message, state: FSMContext) -> None:
    """Сохранение нового клиента, добавленного админом. Окончание AddUserByAdminFSM"""
    contact = message.contact
    tg_id = str(contact.user_id)
    username = "user" + tg_id

    # если пользователь уже есть
    if await app.service.is_user_exists(username):
        data = await state.get_data()
        try:
            await data["prev_mess"].delete()
        except TelegramBadRequest:
            pass
        msg = await message.answer("Пользователь уже существует, отправьте другой контакт",
                                   reply_markup=kb.cancel_keyboard().as_markup())
        await state.update_data(prev_mess=msg)

    # новый пользователь
    else:
        client_model = models.ClientCreate(
            username=username,
            tg_id=tg_id,
            is_active=True,
            expire_time=0   # TODO сейчас стоит 0, то есть неограниченный период для пользователей, добавленных админом
        )

        new_client = await app.service.create_new_client(client_model)

        data = await state.get_data()
        try:
            await data["prev_mess"].delete()
        except TelegramBadRequest:
            pass
        await state.clear()

        # TODO хз как получить ссылку для клиента
        await message.answer(f"Новый клиент <b>\"{new_client.username}\"</b> с неограниченным сроком действия "
                             f"подписки успешно добавлен ✅")
        await main_menu(message)


# CANCEL BUTTON
@router.callback_query(lambda callback: callback.data == "cancel", StateFilter("*"))
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    """Cancel FSM and delete last message"""
    await state.clear()
    await callback.message.answer("Действие отменено ❌")
    await main_menu(callback)
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

