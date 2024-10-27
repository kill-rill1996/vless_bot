import datetime
import uuid
from typing import List

import py3xui
import pytz
from py3xui import AsyncApi

from settings import settings
from models import models


class ClientService:

    def __init__(self):
        self.api = AsyncApi(
            settings.panel_vless.xui_host,
            settings.panel_vless.xui_username,
            settings.panel_vless.xui_password
        )

    async def login(self):
        """Логин по username и password для vless panel"""
        await self.api.login()

    async def get_servers_list(self) -> List[py3xui.Inbound]:
        """Получение списка серверов"""
        servers = await self.api.inbound.get_list()
        return servers

    async def get_clients(self) -> List[models.Client]:
        """Получение клиентов из inbound"""
        server = await self.get_servers_list()
        print("inbound.stream_settings\n\n", server[0].stream_settings)
        clients = server[0].client_stats

        result = []
        for client in clients:
            result.append(models.Client(
                username=client.email,
                tg_id=client.tg_id,
                traffic=await self.get_full_traffic(client.up, client.down),
                is_active=client.enable,
                expire_time=client.expiry_time
            ))

        return result

    async def get_client(self, email) -> models.Client:
        """Получение клиента по username (для vless это email)"""
        client = await self.api.client.get_by_email(email)
        return models.Client(
            username=client.email,
            tg_id=client.tg_id,
            traffic=await self.get_full_traffic(client.up, client.down),
            is_active=client.enable,
            expire_time=client.expiry_time
        )

    async def create_new_client(self, user: models.ClientCreate) -> models.Client:
        """Создание нового клиента"""
        # TODO проверить не существует ли такой уже, возможно она есть в апи

        # создание клиента
        await self.api.client.add(
            settings.panel_vless.inbound_id,
            [py3xui.Client(email=user.username, enable=True,
                           id=str(uuid.uuid4()),
                           flow="xtls-rprx-vision", # TODO: нужно ли
                           expiry_time=int(user.expire_time))]
        )

        # получение нового клиента по email
        new_client = await self.get_client(user.username)


        # TODO connection string
        client = await self.api.client.get_by_email(user.username)
        server = await self.get_servers_list()
        server = server[0]
        connection_string = f"{server.protocol}://{client.sub_id}@{'somedomain123.store'}:{server.port}?type={server.stream_settings.network}&security={server.stream_settings.security}&pbk={server.stream_settings.reality_settings['settings']['publicKey']}&fp={server.stream_settings.reality_settings['settings']['fingerprint']}&sni={server.stream_settings.reality_settings['serverNames'][0]}&sid={server.stream_settings.reality_settings['shortIds'][0]}&spx={'%2F' if server.stream_settings.reality_settings['settings']['spiderX'] == '/' else ''}&flow={client.flow}#{client.email}"
        print("CONNECTION STRING\n\n", connection_string)


        return new_client

    async def is_user_exists(self, username: str) -> bool:
        """Проверка существует ли пользователь"""
        client = await self.api.client.get_by_email(username)

        if client:
            return True
        return False

    @staticmethod
    async def get_full_traffic(download: int, upload: int) -> float:
        """Подсчет потраченного клиентом трафика в Gb"""
        sum_traffic = (download + upload) / settings.panel_vless.traffic_coefficient
        return round(sum_traffic, 2)

    @staticmethod
    async def convert_to_datetime_from_unix(unix_time: float) -> datetime:
        """Перевод unix time в формат ДД.ММ.ГГГГ"""
        timezone = pytz.timezone('Europe/Moscow')
        return datetime.datetime.fromtimestamp(unix_time / 1000, tz=timezone).date().strftime("%d.%m.%Y")


# vless://bf497a8f-a612-44ac-afab-b3f4111c69eb@somedomain123.store:443?type=tcp&security=reality&pbk=_V7Joja7EM0GukBFX7M_HBqtlJAz0hQuYIhoGqWVBwI&fp=chrome&sni=www.google.com&sid=6977dfdb8b9c54&spx=%2F&flow=xtls-rprx-vision#user100
# vless://a30984dc-1a7e-4845-9bbd-0f1c7ad6624e@somedomain123.store:443?type=tcp&security=reality&pbk=_V7Joja7EM0GukBFX7M_HBqtlJAz0hQuYIhoGqWVBwI&fp=chrome&sni=www.google.com&sid=6977dfdb8b9c54&spx=%2F#shuruho
# vless://dd2bd42c-c0f8-4f27-aeb9-a2ecdf42e003@somedomain123.store:443?type=tcp&security=reality&pbk=_V7Joja7EM0GukBFX7M_HBqtlJAz0hQuYIhoGqWVBwI&fp=chrome&sni=www.google.com&sid=6977dfdb8b9c54&spx=%2F#user924250755
# connection_string = f"{inbound.protocol}://{client.id}@{domen}:{port}?type={inbound.stream_settings.network}&security={inbound.stream_settings.security}&pbk={inbound.stream_settings.settings.publicKey}&fp={inbound.stream_settings.settings.fingerprint}&sni={inbound.stream_settings.reality_settings['serverNames'][0]}&sid={inbound.stream_settings.reality_settings['shortIds'][0]}&spx={inbound.stream_settings.settings.spiderX}&flow={client.flow}#{client.email}"

# vless://                                    @somedomain123.store:443?type=tcp&security=reality&pbk=_V7Joja7EM0GukBFX7M_HBqtlJAz0hQuYIhoGqWVBwI&fp=chrome&sni=www.google.com&sid=6977dfdb8b9c54&spx=  /&flow=                #user924250755
# vless://adeb4b33-0268-4cba-9e83-f47260018bc5@somedomain123.store:443?type=tcp&security=reality&pbk=_V7Joja7EM0GukBFX7M_HBqtlJAz0hQuYIhoGqWVBwI&fp=chrome&sni=www.google.com&sid=6977dfdb8b9c54&spx=%2F&flow=xtls-rprx-vision#user924250755
