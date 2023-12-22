from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ciam-demo"
    cognito_domain: str = ""
    cognito_client_id: str = ""
    cognito_client_secret: str = ""
    cognito_redirect_uri: str = ""
    cognito_region: str = ""
    cognito_user_pool_id: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="allow")
