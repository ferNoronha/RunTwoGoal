
from fastapi import APIRouter
from api.schemas.schemas import UserSchema
from api.serializers.userSerializer import UserSerializer
from core.database.db import User as us
from app.oauth2 import require_user

router = APIRouter()


@router.post("/")
def create_user(user: User):
    #cria o usuario
    user_id = len(users)
    users[user_id] = user.dict()
    return {"message": "user created"}

@router.get("/")
def get_users(limit: int = 10, page: int=1, search: str = '', user_id:str = Depends(require_user), ):
    #retorna lista de usuarios
    return {"message":users}

@router.get("/{user_id}")
def read_user(user_id:str):
    #retorna um usuario
    return {"message":"get a user"}

@router.put("/{user_id}")
def read_user(user_id:str, user:User):
    #update usuario
    return {"message":"updated user"}