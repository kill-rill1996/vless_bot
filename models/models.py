from pydantic import BaseModel


class Client(BaseModel):
    username: str
    tg_id: str | None
    traffic: float
    is_active: bool
    expire_time: float

