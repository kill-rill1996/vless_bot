from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PanelVLESS(BaseSettings):
    xui_host: str
    xui_username: str
    xui_password: str
    traffic_coefficient: float = 1073791844.13

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Settings(BaseSettings):
    bot_token: str = Field(validation_alias='TG_TOKEN')
    panel_vless: PanelVLESS = PanelVLESS()

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
