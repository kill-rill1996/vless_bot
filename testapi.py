import requests
from settings import settings

data = {
    "username": settings.panel_vless.xui_username,
    "password": settings.panel_vless.xui_password
}
cookie = requests.post(settings.panel_vless.xui_host + "login", data=data).cookies["3x-ui"]

inbounds = requests.get(settings.panel_vless.xui_host + "panel/api/inbounds/list", cookies={"3x-ui": cookie})
print(inbounds.content)