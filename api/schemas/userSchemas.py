from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from enum import Enum

class UserSchema(BaseModel):
    nome: str
    email: EmailStr
    photo: str
    full_name: str
    role: str | None = None
    active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True

class CreateUserSchema(UserSchema):
    password: constr(min_length=8)
    password_confirm: str
    verified: bool = False

class UserResponseSchema (UserSchema):
    id: str
    pass 

class UserResponse(BaseModel):
    status: str
    user: UserResponseSchema


class FilteredUserResponse(UserSchema):
    id: str

class UserLoginSchemma(BaseModel):
    email: EmailStr
    password: str
