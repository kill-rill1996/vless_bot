from models import models
from routers.utils import convert_to_datetime_from_unix
from settings import settings


async def client_info_message(client: models.Client) -> str:
    """Информация о пользователе 🗓️"""
    # TODO отличать сгенерированный ник и собственный ник в телеграм sep='_user_.'
    # нет tg username
    if settings.id_salt == client.username[:7]:
        tg_id = client.username[7:]
        username = client.username
    # есть tg username
    else:
        username, tg_id = client.username.split(settings.username_salt)

    message = f"👤 Имя: <a href='tg://user?id={tg_id}'>{username}</a>\n"
    message += "✅ Статус: <b>включен</b>\n" if client.is_active else "❌ Статус: <b>отключен</b>\n"
    message += f"📊 Трафик: <b>{client.traffic} Gb</b>\n"
    message += f"🗓 Дата окончания: "

    if client.expire_time != 0:
        expire_date = await convert_to_datetime_from_unix(client.expire_time)
        message += f"<b>{expire_date}</b>"

    else:
        message += "<b>неограниченно ♾</b>"

    message += "\n\n💵 Крайнее пополнение ЧИСЛО на сумму СУММА"

    return message

