
from fastapi import APIRouter, Depends, Request, HTTPException, status, Response
from api.schemas.userSchemas import UserSchema, CreateUserSchema, UserLoginSchemma
from api.serializers.userSerializer import userEntity, userListEntity
from core.database.db import User_db as us
from oauth2 import require_user, AuthJWT
from utils import hash_password, verify_password
from enumConfig import Role
from datetime import datetime, timedelta
from config import settings

router = APIRouter()
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(
    user: CreateUserSchema, 
    request: Request,
    response: Response
    ):
    #verifica se existe
    exist = us.find_one({"email":user.email.lower()})
    if exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already exist")
    
    if user.password != user.password_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong passwords")
    
    user.password = hash_password(user.password)
    del user.password_confirm
    if user.role is None:
        user.role = Role.admin
    else:
        # user.role = Role(user.role.lower()) pega pelo value
        user.role = str(Role[user.role.lower()].value) #pega o value pela key
    user.email = user.email.lower()
    user.created_at = datetime.utcnow()
    user.created_at = user.updated_at

    user.verified = False
    
    result = us.insert_one(user.dict())
    exist = us.find_one({"_id":result.inserted_id})
    if exist:
        return {"status": "success", "message": "Adicionado"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error user creating")


@router.get("/", status_code=status.HTTP_202_ACCEPTED)
def get_users(
    limit: int = 10, 
    page: int=1, 
    search: str = '', 
    user_id:str = Depends(require_user)
    ):
    #retorna lista de usuarios
    skip = (page-1)*limit
    pipeline = [
        {
            {'$match':{}},
            {'$skip':skip},
            {'$limit':limit}

        }
    ]
    list = userListEntity(us.aggregate(pipeline))
    return {'status': 'success', 'results': len(list), 'users': list}

@router.get("/{user_id}")
def read_user(user_id:str):
    #retorna um usuario
    return {"message":"get a user"}

@router.put("/{user_id}")
def read_user(user_id:str, user:UserSchema):
    #update usuario
    return {"message":"updated user"}

@router.post("/login")
def login(
    user: UserLoginSchemma,
    response: Response,
    Authorize: AuthJWT = Depends()
    ):

    exist = us.find_one({"email":user.email})
    if not exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong e-mail or password")
    
    user_entity = userEntity(exist)
    if not user_entity["active"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not active")
    
    if not verify_password(user.password,user_entity["password"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong password")
    
    access_token = Authorize.create_access_token(subject=str(user_entity["id"]),expires_time=timedelta(ACCESS_TOKEN_EXPIRES_IN))
    refresh_token = Authorize.create_refresh_token(subject=str(user_entity["id"]),expires_time=timedelta(REFRESH_TOKEN_EXPIRES_IN))

    response.set_cookie('access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('refresh_token', refresh_token, REFRESH_TOKEN_EXPIRES_IN * 60, REFRESH_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('logged_in', 'True', ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')


    return {'status': 'success', 'access_token': access_token}