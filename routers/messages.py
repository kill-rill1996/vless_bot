from models import models
from routers.utils import convert_to_datetime_from_unix


async def client_info_message(client: models.Client) -> str:
    """Информация о пользователе 🗓️"""

    message = f"👤Имя: {client.username}\n"
    message += "✅ Статус: включен\n" if client.is_active else "❌ Статус: отключен\n"
    message += f"📊Трафик: {client.traffic} Gb\n"
    message += f"🗓Дата окончания: "

    if client.expire_time != 0:
        expire_date = await convert_to_datetime_from_unix(client.expire_time)
        message += f"{expire_date}"

    else:
        message += "неограниченно ♾"

    message += "\n\n💵 Крайнее пополнение ЧИСЛО на сумму СУММА"

    return message

