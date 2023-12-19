from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ciam-demo"
    app_client_id: str = ""
    app_client_secret: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="allow")
