from typing import List, Callable
from functools import wraps

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from models import models
from routers import salt


def back_button(callback_data: str):
    """Декоратор для добавления кнопки "назад" в клавиатуру, принимает callback куда необходимо перейти"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            result.row(InlineKeyboardButton(text="🔙 назад", callback_data=f"{callback_data}"))
            return result
        return wrapper
    return decorator


def main_keyboard() -> InlineKeyboardBuilder:
    """Главная клавиатура"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text="👤 Пользователи", callback_data=f"main{salt}users"),
        InlineKeyboardButton(text="Должники", callback_data=f"main{salt}debtors"),
        InlineKeyboardButton(text="➕ Новый польз.", callback_data=f"main{salt}new-user"),
        InlineKeyboardButton(text="Операции", callback_data=f"main{salt}operations"),
        InlineKeyboardButton(text="🗑️ Удалить польз.", callback_data=f"main{salt}delete-user")
                 )

    keyboard.adjust(2)
    return keyboard


@back_button(callback_data="back-to-menu")
def all_users_keyboard(users: List[models.Client]) -> InlineKeyboardBuilder:
    """Клавиатура со всеми пользователями"""
    keyboard = InlineKeyboardBuilder()
    for user in users:

        keyboard.row(
            InlineKeyboardButton(text=f"{user.username}", callback_data=f"user{salt}{user.username}")
        )

    keyboard.adjust(2)

    return keyboard


@back_button(callback_data=f"main{salt}users")
def user_keyboard(user: models.Client) -> InlineKeyboardBuilder:
    """Вывод информации по одному пользователю"""
    keyboard = InlineKeyboardBuilder()

    lock_callback = ("Заблокировать", "lock") if user.is_active else ("Разблокировать", "unlock")

    keyboard.row(
        InlineKeyboardButton(text="Пополнения", callback_data=f"user-operations{salt}{user.username}"),
        InlineKeyboardButton(text=lock_callback[0], callback_data=f"user-lock{salt}{lock_callback[1]}{salt}{user.username}"),
        InlineKeyboardButton(text="Редактировать", callback_data=f"user-edit{salt}{user.username}"),
        InlineKeyboardButton(text="Удалить", callback_data=f"user-delete{salt}{user.username}")
    )
    keyboard.adjust(2)
    return keyboard


@back_button(f"main{salt}delete-user")
def delete_keyboard(data: str) -> InlineKeyboardBuilder:
    """Кнопка удалить под сообщением"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="Удалить", callback_data=f"delete{salt}{data}"),
    )

    return keyboard


def confirm_keyboard(data: str) -> InlineKeyboardBuilder:
    """Клавиатура подтверждения"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="Да", callback_data=f"yes{salt}{data}"),
        InlineKeyboardButton(text="Нет", callback_data=f"no{salt}{data}"),
    )

    keyboard.adjust(2)
    return keyboard



def back_keyboard(callback_data: str) -> InlineKeyboardBuilder:
    """Шаблон клавиатуры для возвращения к определенному сообщению"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="🔙 назад", callback_data=f"{callback_data}"))
    return keyboard


def cancel_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура для отмены создания пользователя админом"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel"))
    return keyboard
