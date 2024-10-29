import uuid
import requests
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

    async def get_client(self, username) -> models.Client:
        """Получение клиента по username (для vless это email)"""
        client = await self.api.client.get_by_email(username)
        return models.Client(
            username=client.email,
            tg_id=client.tg_id,
            traffic=await self.get_full_traffic(client.up, client.down),
            is_active=client.enable,
            expire_time=client.expiry_time
        )

    async def create_new_client(self, user: models.ClientCreate) -> (models.ClientWithKey | None, dict | None):
        """Создание нового клиента и строки для подключения
        (в случае дублирования пользователя возвращает None и Error с ошибкой)"""
        # проверка существования пользователя
        if await self.is_user_exists(user.username):
            return None, models.Error(message="user already exists")

        # создание клиента
        new_uuid = str(uuid.uuid4())
        await self.api.client.add(
            settings.panel_vless.inbound_id,
            [py3xui.Client(email=user.username,
                           enable=True,
                           tg_id=user.tg_id,
                           id=new_uuid,
                           flow=settings.panel_vless.flow,
                           # TODO не потерять строку с правильным формирование времени
                           # expire_time = int((datetime.now(tz=pytz.timezone("Europe/Moscow")) + timedelta(days=30)).timestamp() * 1000)
                           expiry_time=user.expire_time)]
        )

        # получение нового клиента по email
        new_client = await self.get_client(user.username)

        # получение строки для подключения
        key = await self._get_key(new_uuid)
        new_client_with_key = models.ClientWithKey(key=key, **new_client.dict())

        return new_client_with_key, None

    async def delete_client(self, username: str) -> None:
        """Удаление клиента из сервиса"""
        client = await self.api.client.get_by_email(username)
        print(client.id)

        await self.api.client.delete(settings.panel_vless.inbound_id, "71f35540-8351-44ae-8677-75fc8115a5a4")

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

    async def lock_unlock_client(self, username: str, action: str) -> models.Client:
        """Блокировка и разблокировка клиента"""
        print(username)
        client: py3xui.Client = await self.api.client.get_by_email(username)
        print(client)
        print(action)

        if action == "lock":
            client.email = "someemailgmail.com"
        else:
            client.enable = True
        await self.api.client.update("b6f50b1b-138e-4ebc-8fd8-e47a1d2dabff", client)

        updated_client: models.Client = await self.get_client(username)
        return updated_client

    @staticmethod
    async def get_full_traffic(download: int, upload: int) -> float:
        """Подсчет потраченного клиентом трафика в Gb"""
        sum_traffic = (download + upload) / settings.panel_vless.traffic_coefficient
        return round(sum_traffic, 2)




