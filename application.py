from pydantic import BaseModel
from pydantic_settings import BaseSettings

from service.service import ClientService
from settings import settings


class App(BaseModel):
    service: ClientService = ClientService()
    db: None = None
    settings: BaseSettings = settings

    class Config:  # Разрешение использования нестандартного типа
        arbitrary_types_allowed = True


def get_app():
    return App()
