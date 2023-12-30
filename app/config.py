from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path
from fastapi.templating import Jinja2Templates


class AppSettings(BaseSettings):
    app_name: str = "ciam-demo"
    cognito_domain: str = ""
    cognito_client_id: str = ""
    cognito_client_secret: str = ""
    cognito_redirect_uri: str = ""
    cognito_logout_redirect_uri: str = ""
    cognito_region: str = ""
    cognito_user_pool_id: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


@lru_cache
def get_app_settings():
    return AppSettings()


templates = Jinja2Templates(directory=Path.cwd() / "app" / "templates")
