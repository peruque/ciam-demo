from pydantic import BaseModel


class UserInfo(BaseModel):
    id: str
    username: str
    first_name: str
    last_name: str
    email: str
    groups: list[str]


class AccessTokenPayload(BaseModel):
    sub: str
    username: str
    groups: list[str]
    token: str
