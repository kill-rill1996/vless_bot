from pydantic import BaseModel


class ClientCreate(BaseModel):
    """Для создания клиента в панели 3x-ui"""
    username: str
    tg_id: str | None
    is_active: bool
    expire_time: float


class Client(ClientCreate):
    traffic: float

