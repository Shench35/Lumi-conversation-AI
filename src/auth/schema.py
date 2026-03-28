from pydantic import BaseModel
from typing import List


class LoginModel(BaseModel):
    email: str
    password: str

class CreateUserModel(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str


class EmailModel(BaseModel):
    addresses : List[str]