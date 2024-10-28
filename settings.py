from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PanelVLESS(BaseSettings):
    xui_host: str
    xui_username: str
    xui_password: str
    traffic_coefficient: float = 1073791844.13
    domain: str
    flow: str = "xtls-rprx-vision"
    inbound_id: int = 1  # TODO подумать куда лучше убрать

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Settings(BaseSettings):
    bot_token: str = Field(validation_alias='TG_TOKEN')
    panel_vless: PanelVLESS = PanelVLESS()
    salt: str = "#&*!@"
    id_salt: str = "_user_."
    username_salt: str = "__id__"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
