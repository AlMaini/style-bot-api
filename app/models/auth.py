from typing import Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    message: str
    user_id: str
    email: str
    access_token: str
    refresh_token: str
    expires_in: int


class SignupResponse(BaseModel):
    message: str
    user_id: str
    email: str
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None
    expires_in: Optional[str] = None
