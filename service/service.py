import uuid
from typing import List

import py3xui
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

    async def get_inbound_list(self) -> List[py3xui.Inbound]:
        """Получение списка серверов"""
        servers = await self.api.inbound.get_list()
        return servers

    async def get_clients(self) -> List[models.Client]:
        """Получение клиентов из inbound"""
        server = await self.get_inbound_list()
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

    async def create_new_client(self, user: models.ClientCreate) -> (models.Client, str):
        """Создание нового клиента и строки для подключения"""
        # создание клиента
        new_uuid = str(uuid.uuid4())
        await self.api.client.add(
            settings.panel_vless.inbound_id,
            [py3xui.Client(email=user.username,
                           enable=True,
                           tg_id=user.tg_id,
                           id=new_uuid,
                           flow=settings.panel_vless.flow,
                           expiry_time=user.expire_time)]
        )

        # получение нового клиента по email
        new_client = await self.get_client(user.username)

        # получение строки для подключения
        key = await self._get_key(new_uuid)
        new_client_with_key = models.ClientWithKey(key=key, **new_client.dict())

        return new_client_with_key

    async def _get_key(self, client_uuid: str) -> str:
        """Создание строки подключения"""
        server = await self.get_inbound_list()
        server = server[0]

        key = f"{server.protocol}://{client_uuid}@{settings.panel_vless.domain}:{server.port}" \
              f"?type={server.stream_settings.network}" \
              f"&security={server.stream_settings.security}" \
              f"&pbk={server.stream_settings.reality_settings['settings']['publicKey']}" \
              f"&fp={server.stream_settings.reality_settings['settings']['fingerprint']}" \
              f"&sni={server.stream_settings.reality_settings['serverNames'][0]}" \
              f"&sid={server.stream_settings.reality_settings['shortIds'][0]}" \
              f"&spx={'%2F' if server.stream_settings.reality_settings['settings']['spiderX'] == '/' else ''}" \
              f"&flow={settings.panel_vless.flow}"

        return key

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




