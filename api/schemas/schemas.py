from pydantic import BaseModel, EmailStr, constr
from datetime import datetime


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
    verified: bool = True

class UserResponseSchema (UserSchema):
    id: str
    pass 

class UserResponse(BaseModel):
    status: str
    user: UserResponseSchema


class FilteredUserResponse(UserSchema):
    id: str

# class User(BaseModel):
#     email: EmailStr
#     username: str
#     password: str
#     full_name: str
#     active: bool=True
