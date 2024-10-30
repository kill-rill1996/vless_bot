from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

import routers.keyboards as kb
from routers.fsm_states import AddUserByAdminFSM, DeleteUserFSM
from routers.middlewares import CheckIsAdminMiddleware, CheckPrivateMessageMiddleware
from routers import app, salt, messages as ms
from models import models
from settings import settings

router = Router()
router.message.middleware.register(CheckPrivateMessageMiddleware())
router.message.middleware.register(CheckIsAdminMiddleware(settings.admins))


@router.message(Command("start"))
async def start_message(message: types.Message) -> None:
    """Команда /start"""
    msg = "Hello message"
    if type(message) == types.Message:
        await message.answer(msg)   # TODO add stickers

    await app.service.login()

    await main_menu(message)


@router.callback_query(lambda callback: callback.data == "back-to-menu")
@router.message(Command("menu"))
async def main_menu(message: types.Message | types.CallbackQuery, state: FSMContext = None):
    """Главное меню"""
    if state != None:
        await state.clear()

    msg = "Главное меню"
    if type(message) == types.Message:
        # await state.clear()  # для сброса state в случае перехода по кнопке /menu из любой точки бота
        await message.answer(msg, reply_markup=kb.main_keyboard().as_markup())
    else:
        # при отмене
        if message.data == "cancel":
            await message.message.answer(msg, reply_markup=kb.main_keyboard().as_markup())
        # при нажатии кнопки назад
        else:
            # await state.clear()  # для сброса state в случае перехода по кнопке назад
            await message.message.edit_text(msg, reply_markup=kb.main_keyboard().as_markup())


@router.callback_query(lambda callback: callback.data != "cancel" and callback.data.split(salt)[1] == "users")
async def all_users_handler(callback: types.CallbackQuery) -> None:
    """Выводит всех пользователей"""
    all_users = await app.service.get_clients()

    await callback.message.edit_text("Список пользователей:", reply_markup=kb.all_users_keyboard(all_users).as_markup())


@router.callback_query(lambda callback: callback.data != "cancel" and callback.data.split(salt)[0] == "user",
                       StateFilter(None))
async def get_user_info_handler(callback: types.CallbackQuery) -> None:
    """Вывод информации по пользователю"""
    username = callback.data.split(salt)[1]
    client = await app.service.get_client(username)

    msg = await ms.client_info_message(client)
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
    username = app.settings.id_salt + tg_id

    client_model = models.ClientCreate(
        username=username,
        tg_id=tg_id,
        is_active=True,
        expire_time=0
    )

    new_client_with_key, error = await app.service.create_new_client(client_model)

    # если пользователь уже есть
    if error:
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
        data = await state.get_data()
        try:
            await data["prev_mess"].delete()
        except TelegramBadRequest:
            pass
        await state.clear()

        await message.answer(f"Новый клиент <b>\"{new_client_with_key.username}\"</b> с неограниченным сроком действия "
                             f"подписки успешно добавлен ✅\n\n<b>Следующим сообщением будет отправлена ссылка на подключение</b>")
        await message.answer(new_client_with_key.key)

        await main_menu(message)


# DELETE USER
@router.callback_query(lambda callback: callback.data != "cancel" and callback.data.split(salt)[1] == "delete-user")
async def delete_user(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Вывод пользователей"""
    all_clients = await app.service.get_clients()
    await state.set_state(DeleteUserFSM.start)

    await callback.message.edit_text("Выберите пользователя для удаления:",
                                     reply_markup=kb.all_users_keyboard(all_clients).as_markup())


@router.callback_query(DeleteUserFSM.start)
async def delete_user(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Вывод пользователей"""
    client_username = callback.data.split(salt)[1]
    client = await app.service.get_client(client_username)

    await state.set_state(DeleteUserFSM.client)

    message = await ms.client_info_message(client)

    await callback.message.edit_text(message,
                                     reply_markup=kb.delete_keyboard(client_username).as_markup())


@router.callback_query(DeleteUserFSM.client)
async def confirmation_delete_user(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Подтверждение удаления пользователя"""
    await state.set_state(DeleteUserFSM.confirm)

    client_username = callback.data.split(salt)[1]

    message = await ms.confirm_delete_client_message(client_username)

    await callback.message.edit_text(message,
                                     reply_markup=kb.confirm_keyboard(client_username).as_markup())


@router.callback_query(DeleteUserFSM.confirm, lambda callback: callback.data.split(salt)[0] in ["yes", "no"])
async def delete_user_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Удаление пользователя"""
    await state.clear()

    # отмена удаления
    if callback.data.split(salt)[0] == "no":
        await callback.message.edit_text(f"Действие отменено ❌")
        await callback.message.answer("Главное меню", reply_markup=kb.main_keyboard().as_markup())
        return

    # удаляем
    username = callback.data.split(salt)[1]
    await app.service.delete_client(username)

    await callback.message.edit_text(f"Клиент {username} удален ✅")
    await callback.message.answer("Главное меню", reply_markup=kb.main_keyboard().as_markup())


# LOCK CLIENT
@router.callback_query(lambda callback: callback.data != "cancel" and
                      (callback.data.split(salt)[0] == "user-lock" or callback.data.split(salt)[0] == "user-unlock"))
async def lock_unlock_client_handler(callback: types.CallbackQuery):
    callback_data = callback.data.split(salt)
    action = callback_data[0].split("-")[1] # "lock" / "unlock"
    username = callback_data[1]

    # выполнение блокировки или разблокировки в зависимости от action ("lock" / "unlock")
    updated_client = await app.service.lock_unlock_client(username, action)

    msg = await ms.client_info_message(updated_client)
    await callback.message.answer(msg, reply_markup=kb.user_keyboard(updated_client).as_markup())


# HELP MESSAGE
@router.message(Command("help"))
async def help_handler(message: types.Message) -> None:
    """Help message"""
    msg = ms.get_help_message()
    await message.answer(msg)


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

