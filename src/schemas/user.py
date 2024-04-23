import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserReadSchema(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    avatar: str
    role: str
    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=12)


class UserUpdateSchema(BaseModel):
    username: Optional[str] = Field(min_length=3, max_length=50)
    email: Optional[EmailStr]


class UserResponseSchema(BaseModel):
    user: UserReadSchema
    detail: str = "User successfully created."


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    result: str


class RequestEmail(BaseModel):
    email: EmailStr


class RequestNewPassword(BaseModel):
    new_password: str = Field(min_length=6, max_length=12)