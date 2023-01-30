from pydantic import BaseModel, EmailStr

class User(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    active: bool=True
