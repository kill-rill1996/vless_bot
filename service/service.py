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
        await self.api.login()

    async def get_servers_list(self) -> List[py3xui.Inbound]:
        servers = await self.api.inbound.get_list()
        return servers

    async def get_clients(self) -> List[models.Client]:
        """Получение клиентов из inbound"""
        server = await self.get_servers_list()
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

        print(result)
        return result

    async def get_client(self, email) -> models.Client:
        client = await self.api.client.get_by_email(email)
        return models.Client(
            username=client.email,
            tg_id=client.tg_id,
            traffic=await self.get_full_traffic(client.up, client.down),
            is_active=client.enable,
            expire_time=client.expiry_time
        )

    async def create_new_client(self, user: models.ClientCreate) -> models.Client:
        # TODO проверить не существует ли такой уже, возможно она есть в апи

        # создание клиента
        await self.api.client.add(
            settings.panel_vless.inbound_id,
            [py3xui.Client(email=user.username, enable=True,
                           id=str(uuid.uuid4()),
                           expiry_time=int(user.expire_time))]
        )

        # получение нового клиента по email
        new_client = await self.get_client(user.username)
        return new_client

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






