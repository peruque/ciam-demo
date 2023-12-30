from pydantic import BaseModel


class UserInfo(BaseModel):
    id: str
    username: str
    first_name: str
    last_name: str
    email: str
