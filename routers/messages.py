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


async def confirm_delete_client_message(username: str) -> str:
    """Сообщение об удалении клиента"""
    message = f"Удалить пользователя \"{username}\"?"
    return message


def get_help_message() -> str:
    """Help message"""
    message = "<b>Возможности бота:</b>\n" \
              "- Предоставляет функционал по управлению подписками\n" \
              "- Позволяет получать информацию о пользователях, которые получили подписку\n\n" \
              "<b>Инструкция использования:</b>\n" \
              "- Для перехода в главное меню отправьте команду /menu\n" \
              "- Для просмотра списка пользователей и информации о них перейдите в главное меню и нажмите \"👤 Пользователи\", " \
              "выберите пользователя, о котором хотите посмотреть информацию (ссылку на чат, срок истечения подписки, трафик, операции)\n" \
              "- Для добавления нового пользователя с неограниченным сроком подписки перейдите в главное меню " \
              "и нажмите \"➕ Новый польз.\", далее отправьте карточку контакта необходимого пользователя\n" \
              "- Для просмотра списка должников и операций в главном меню нажмите \"Должники\" и \"Операции\" соответственно"

    return message
