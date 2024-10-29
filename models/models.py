from pydantic import BaseModel


class ClientCreate(BaseModel):
    """Для создания клиента в панели 3x-ui"""
    username: str
    tg_id: str | None
    is_active: bool
    expire_time: int


class Client(ClientCreate):
    """Для вывода клиента для пользователей"""
    traffic: float


class ClientWithKey(Client):
    """Для вывода клиента с ключом при создании"""
    key: str


class Error(BaseModel):
    """Ошибки от Services"""
    message: str

