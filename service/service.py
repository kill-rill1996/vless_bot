from typing import List

import py3xui
from py3xui import AsyncApi

from settings import settings


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

    async def get_clients(self) -> List[py3xui.Client]:
        """Получение клиентов из inbound"""
        server = await self.get_servers_list()
        clients = server[0].client_stats
        print(clients)
        return clients

    async def get_client(self, email) -> py3xui.Client:
        client = await self.api.client.get_by_email(email)
        return client





