from datetime import datetime

import pytz
from aiogram import Router, types, F
from aiogram.filters import Command

from service import client_service
from settings import settings


router = Router()
# router.message.middleware.register(CheckPrivateMessageMiddleware())


@router.message(Command("start"))
async def start_message(message: types.Message) -> None:
    """Команда /start"""
    await message.answer("Для управления подпиской на канал выберите команду /menu во вкладке \"Меню\" или "
                         "нажмите на команду прямо в сообщении.\n\n"
                         "Для просмотра инструкции и обращения в поддержку выберите команду /help")


@router.message(F.text == "Тест")
async def test_handler(message: types.Message) -> None:
    """Test"""

    await client_service.login()
    # servers = await client_service.get_servers_list()
    # client = await client_service.get_client("sanya_dop")
    clients = await client_service.get_clients()

    timezone = pytz.timezone('Europe/Moscow')
    dt_object = datetime.fromtimestamp(clients[0].expiry_time / 1000, tz=timezone)
    print("Datetime with Timezone:", dt_object)
    await message.answer(f"Выполняется тестовое действие")
    await message.answer(f"servers:\n\n{clients}")

