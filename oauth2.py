import base64
from typing import List
from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from bson.objectid import ObjectId
from enumConfig import Role
from api.serializers.userSerializer import userEntity, userRoleEntity

from core.database.db import User_db
from config import settings


class Settings(BaseModel):
    authjwt_algorithm: str = settings.JWT_ALGORITHM
    authjwt_decode_algorithms: List[str] = [settings.JWT_ALGORITHM]
    authjwt_token_location: set = {'cookies', 'headers'}
    authjwt_access_cookie_key: str = 'access_token'
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_cookie_csrf_protect: bool = False
    authjwt_public_key: str = base64.b64decode(
        settings.JWT_PUBLIC_KEY).decode('utf-8')
    authjwt_private_key: str = base64.b64decode(
        settings.JWT_PRIVATE_KEY).decode('utf-8')


@AuthJWT.load_config
def get_config():
    return Settings()


class NotVerified(Exception):
    pass


class UserNotFound(Exception):
    pass

class NotActive(Exception):
    pass

class NotAdmin(Exception):
    pass

def role(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()

    user_role = userRoleEntity(User_db.find_one({'_id': ObjectId(str(user_id))}))
    return user_role    

def admin_role(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()

        user_role = userRoleEntity(User_db.find_one({'_id': ObjectId(str(user_id))}))
        
        
        if Role(int(user_role["role"])) != Role.admin:
            print("entrou")
            raise NotAdmin("User role")
        
    except Exception as e:
        errors(e)
        
    return True

def require_user(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()
        user = userEntity(User_db.find_one({'_id': ObjectId(str(user_id))}))

        if not user:
            raise UserNotFound('User no longer exist')

        # if not user["verified"]:
        #     raise NotVerified('You are not verified')
        
        if not user["active"]:
            raise NotActive('You are not active')

    except Exception as e:
        errors(e)
    return user_id

def raise_errors(user):
    if not user:
        raise UserNotFound('User no longer exist')
    if not user["verified"]:
        raise NotVerified('You are not verified')
    if not user["active"]:
        raise NotActive('You are not active')

def errors(e):
    error = e.__class__.__name__
    print(error)
    if error == 'MissingTokenError':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='You are not logged in')
    if error == 'UserNotFound':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='User no longer exist')
    if error == 'NotVerified':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Please verify your account')
    if error == "NotAdmin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='User Role')
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is invalid or has expired')
